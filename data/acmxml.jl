using LightXML, Dates, TimeZones, Match, Distributed

df = DateFormat("y/m/d H:M")
op_df = DateFormat("yyyy-mm-dd HH:MM:SS")

xdoc = parse_file("../Downloads/false (4).xml");
xroot = root(xdoc)
timeslots = Iterators.flatten(Iterators.map(x->Iterators.filter(y->name(y) == "timeslot", child_elements(x)), Iterators.filter(x->name(x) == "subevent", child_elements(xroot))))
timezone = TimeZone(content(xroot["timezone_id"][1]))
utc = tz"UTC"

struct Author
	first_name::String
	last_name::String
end

struct ConferenceEvent
	title::String
	event_id::String
	tstart::ZonedDateTime
	tend::ZonedDateTime
	room::String
	track::String
	authors::Vector{Author}
end

abstract type ScheduleInfo end
struct StandardTalk <: ScheduleInfo end
struct ZoomTalk <: ScheduleInfo end
struct NotStreamed <: ScheduleInfo end

parse_authors(persons) = 
	if length(persons) > 0 
		return collect(Iterators.map(person->Author(content(person["first_name"][1]), content(person["last_name"][1])), child_elements(persons[1])))
	else 
		return []
	end

events = Iterators.map(x->begin 
	start_date = ZonedDateTime(DateTime("$(content(x["date"][1])) $(content(x["start_time"][1]))", df), timezone)
	end_date = ZonedDateTime(DateTime("$(content(x["date"][1])) $(content(x["end_time"][1]))", df), timezone)
	if end_date < start_date
		end_date += Dates.Day(1)
	end
	ConferenceEvent(
	content(x["title"][1]), 
	content(x["event_id"][1]), 
	start_date, 
	end_date, 
	content(get(x["room"], 1, nothing)),
	content(x["tracks"][1]["track"][1]),
	parse_authors(x["persons"])) end, Iterators.filter(x->get(x["event_id"], 1, nothing) != nothing, timeslots))


function make_schedule(events, schedulers)
	scheduling = Dict{ConferenceEvent, Union{ScheduleInfo, Nothing}}()

	min_start_time = nothing
	for event in events
		scheduled = nothing
		for scheduler in schedulers
			assignment = scheduler(event)
			if !isnothing(assignment)
				scheduled = assignment
			end
		end
		scheduling[event] = scheduled

		if isnothing(min_start_time) || event.tstart < min_start_time
			min_start_time = event.tstart
		end
	end


	desired_start_time = now(utc)
	offs = min_start_time - desired_start_time
	warp_schedule = Dict{ConferenceEvent, Union{ScheduleInfo, Nothing}}()

	for (evt, assgn) in scheduling
		nevt = ConferenceEvent(evt.title, evt.event_id, evt.tstart - offs, evt.tend - offs, evt.room, evt.track, evt.authors)
		warp_schedule[nevt] = assgn
	end

	return warp_schedule

	return scheduling
end

# track construction
abstract type PlaybackElement end
struct Recorded <: PlaybackElement
	src::String
	caption_src::Union{String, Nothing}
	duration::Int
	Recorded(src::String, caption_src=nothing, duration=-1) = new(src,caption_src,duration)
end
struct Streamed <: PlaybackElement 
	name::String
end
struct Playlist
	name::String
	stream::String
	tstart::ZonedDateTime
	tend::ZonedDateTime
	items::Vector{PlaybackElement}
	repeat::Bool
end 

# make into sequential streams
function make_timeline(playlists)
	timeline = Dict{String, Vector{Playlist}}()
	for playlist in playlists
		if isnothing(playlist[2]) continue end
		push!(get!(timeline, playlist[2].stream, Playlist[]), playlist[2])
	end
	for trk in timeline
		sort!(trk[2], by=(a)->a.tstart)
	end
	return timeline
end
# fill in empty parts of the schedule with the filler video
function fill_timeline(timeline, fillergen)
	out_timeline = Dict{String, Vector{Playlist}}()
	for (track,evts) in timeline
		out_evts = Vector{Playlist}()
		last_end_time = nothing
		for evt in evts
			if isnothing(last_end_time) # don't fill until the start of the track
				push!(out_evts, evt)
				last_end_time = evt.tend 
				continue
			end
			delta = evt.tstart - last_end_time
			if delta.value > 100 # ms
				push!(out_evts, fillergen(track, last_end_time, evt.tstart))
			end
			push!(out_evts, evt)
			last_end_time = evt.tend
		end
		out_timeline[track] = out_evts
	end
	return out_timeline
end

function highspeed_timeline(timeline)
	# this makes every event have a 5 second intro, 25 seconds of talk, followed by a 10 second transistion and a 5 second Q&A session. Filler sections are reduced to 45 seconds
	out_timeline = Dict{String, Vector{Playlist}}()
	for (track, evts) in timeline
		out_evts = Vector{Playlist}()

		track_cumulative_offset = Second(0)
		for playlist in evts
			orig_vid_dur = playlist.tend - playlist.tstart
			new_dur = Second(45)
			delta_end = orig_vid_dur - new_dur

			items = PlaybackElement[]
			for item in playlist.items
				if item isa Recorded && item.caption_src != nothing
					push!(items, Recorded(item.src, item.caption_src, 25))
				else
					push!(items, item)
				end
			end

			evt = Playlist(playlist.name, playlist.stream, playlist.tstart - track_cumulative_offset, playlist.tend - track_cumulative_offset - delta_end, items, playlist.repeat)
			track_cumulative_offset += delta_end
			push!(out_evts, evt)
		end
		out_timeline[track] = out_evts
	end
	return out_timeline
end

# writes the schedule to a SMIL file (of our own internal format)
function format_time_for_smil(time::ZonedDateTime)
	in_utc = astimezone(time, utc)
	return Dates.format(in_utc, op_df)
end

function make_vid_el(plist, vel::Recorded)
	vid_elem = new_child(plist, "video")
	set_attributes(vid_elem, Dict(
		"src"=>"mp4:$(vel.src)",
		"start"=>0,
		"length"=>vel.duration))
	if !isnothing(vel.caption_src)
		set_attribute(vid_elem, "captions", vel.caption_src)
	end
end
function make_vid_el(plist, vel::Streamed)
	vid_elem = new_child(plist, "video")
	set_attributes(vid_elem, Dict(
		"src"=>"$(vel.name)",
		"start"=>-2,
		"length"=>-1))
end

function make_smil(timeline)
	xdoc = XMLDocument()
	xroot = create_root(xdoc, "smil")
	new_child(xroot, "head") # needs to be here, but is just filler
	body = new_child(xroot, "body")
	for (stream, playlists) in timeline
		str_elem = new_child(body, "stream")
		set_attribute(str_elem, "name", stream)
		for pl in playlists
			plist = new_child(body, "playlist")
			set_attributes(plist, Dict("name"=>pl.name, 
				"playOnStream"=>pl.stream, 
				"repeat"=>pl.repeat, 
				"scheduled"=>format_time_for_smil(pl.tstart)))
			for vel in pl.items 
				make_vid_el(plist, vel)
			end
		end
	end
	return xdoc
end

using DataFrames, DataFramesMeta
function generate_schedule_csv(out)
	df = DataFrame(title=String[], room=String[], track=String[], tstart=ZonedDateTime[], tend=ZonedDateTime[])
	rows = map(x->(x.title, x.room, x.track, x.tstart, x.tend), unique(keys(out)))
	for row in rows
		push!(df, row)
	end

	return @linq df |> orderby(:room, :tstart) |> select(title=:title, room=:room, track=:track, tstart=format_time_for_smil.(:tstart), tend=format_time_for_smil.(:tend))
end


function generate_title_video(event, ::StandardTalk, outdir)
	duration = Dates.toms(event.tend - event.tstart - Minute(5))/1000
	authors =  join(["$(author.first_name) $(author.last_name)" for author in event.authors], ", ")
	title = "$(event.title)\n$(authors)\n$(event.tstart) - $(event.tend)"
	tfile = "$(event.event_id).txt"
	pfile = "$(event.event_id).png"
	open(joinpath(outdir, tfile), "w") do io
    	write(io, title)
    end
	ofile = "$(event.event_id).mp4"
	tfr = replace(replace(joinpath(outdir, tfile), "\\" =>"\\\\\\\\"), ":"=>"\\\\:")



	magickcall = `magick convert -background blue -fill white -font Consolas -size 1920x1080 -gravity center -pointsize 48 label:@$(joinpath(outdir, tfile)) $(joinpath(outdir, pfile))`

	ffcall = `ffmpeg -y -loop 1 -framerate 30 -i $(joinpath(outdir, pfile)) -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -af "aresample=async=1:min_hard_comp=0.100000:first_pts=0" -g 60 -c:v libx264 -r 30 -t 15 -pix_fmt yuv420p $(joinpath(outdir, ofile))`
	return [magickcall, ffcall]
end

function generate_title_video(event, othw, outdir)
	# other kinds of event don't have a prerecorded video attached
	return nothing
end
@everywhere video_gen_job(cmd) = run.(cmd)

function generate_title_videos(schedule, outdir, nprocs)	
	cmds = filter(x->!isnothing(x), [generate_title_video(event, tpe, outdir) for (event, tpe) in schedule])
	pmap(video_gen_job, cmds)
end


function generate_test_video(event, ::StandardTalk, outdir)
	duration = Dates.toms(event.tend - event.tstart - Minute(5))/1000
	authors =  join(["$(author.first_name) $(author.last_name)" for author in event.authors], ", ")
	title = "$(event.title)\n$(authors)\n$(event.tstart) - $(event.tend)"
	tfile = "$(event.event_id).txt"
	pfile = "$(event.event_id).png"
	open(joinpath(outdir, tfile), "w") do io
    	write(io, title)
    end
	ofile = "$(event.event_id).mp4"
	tfr = replace(replace(joinpath(outdir, tfile), "\\" =>"\\\\\\\\"), ":"=>"\\\\:")

	magickcall = `magick convert -background white -fill black -font Consolas -size 1920x1080 -gravity center -pointsize 48 label:@$(joinpath(outdir, tfile)) $(joinpath(outdir, pfile))`

	ffcall = `ffmpeg -y -loop 1 -framerate 30 -i $(joinpath(outdir, pfile)) -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -af "aresample=async=1:min_hard_comp=0.100000:first_pts=0" -g 60 -c:v libx264 -r 30 -t 25 -pix_fmt yuv420p $(joinpath(outdir, ofile))`
	return [magickcall, ffcall]
end

function generate_test_video(event, othw, outdir)
	# other kinds of event don't have a prerecorded video attached
	return nothing
end
function generate_test_videos(schedule, outdir, nprocs)	
	cmds = filter(x->!isnothing(x), [generate_test_video(event, tpe, outdir) for (event, tpe) in schedule])
	pmap(video_gen_job, cmds)
end

# todo validation:
# ALL VIDEOS NOT NAMED "filler" ARE CONSIDERED TALKS
# ALL TALKS MUST EITHER:
#   be streamed
#   have an EXISTING caption file
# ALL VIDEOS MUST EXIST
# ALL VIDEOS MUST BE SHORTER THAN THE TIME ALLOCATED
# NO EVENTS MAY OVERLAP

# scheduling gubbins
# the streams to schedule onto
output_stream_assignment = Dict("Online | OOPSLA/ECOOP" => "OOPSLA_ECOOP", "Online | Rebase" => "REBASE", "Online | SPLASH" => "SPLASH")
# the zoom room strams associated with each track
input_stream_assignment = Dict("Online | OOPSLA/ECOOP" => "ZOOM_OOPSLA_ECOOP", "Online | Rebase" => "ZOOM_REBASE", "Online | SPLASH" => "ZOOM_SPLASH")

# how to schedule talks of specific types
schedule(st, ::StandardTalk) = 
		Playlist(st.event_id, output_stream_assignment[st.room], st.tstart, st.tend, 
			[Recorded("store/titlevids/$(st.event_id).mp4", nothing), 
			Recorded("store/testvids/$(st.event_id).mp4", "store/testvids/$(st.event_id).srt"), 
			Recorded("store/splash_qa.mp4", nothing),
			Streamed(input_stream_assignment[st.room])], false)
schedule(st, ::ZoomTalk) = 
		Playlist(st.event_id, output_stream_assignment[st.room], st.tstart, st.tend,  
			[Streamed(input_stream_assignment[st.room])], false)
schedule(st, ::NotStreamed) = nothing
schedule(st, ::Nothing) = throw("Unhandled talk! $(st)")

# how to fill time
fillergen(stream::String, stime::ZonedDateTime, etime::ZonedDateTime) = Playlist("filler", stream, stime, etime, 
	[Recorded("store/splash_break.mp4", nothing)], true)

# assign by type of event
by_track(event) = @match event begin
	ConferenceEvent(_, _, _, _, "Online | OOPSLA/ECOOP", _, _) => StandardTalk()
	ConferenceEvent(_, _, _, _, "Online | Rebase", _, _) => ZoomTalk()
	ConferenceEvent(_, _, _, _, "Online | SPLASH", "SLE (Software Language Engineering) 2020", _) => StandardTalk()
	ConferenceEvent(_, _, _, _, "Online | SPLASH", "GPCE 2020 - 19th International Conference on Generative Programming: Concepts & Experiences", _) => StandardTalk()
	ConferenceEvent(_, _, _, _, "Online | SPLASH", "SAS 2020 - 27th Static Analysis Symposium", _) => StandardTalk()
	ConferenceEvent(_, _, _, _, "Online | SPLASH", "Dynamic Languages Symposium", _) => StandardTalk()
	ConferenceEvent(_, _, _, _, "Online | SPLASH", "SLE (Software Language Engineering) 2020", _) => StandardTalk()
	ConferenceEvent(_, _, _, _, "Online | SPLASH", "PL Mentoring Workshop (PLMW)", _) => NotStreamed()
	ConferenceEvent(_, _, _, _, "Online | SPLASH", "OOPSLA", _) => StandardTalk()
	ConferenceEvent(_, _, _, _, "Online | PLMW", _, _) => NotStreamed()
	ConferenceEvent(_, _, _, _, "Online | SPLASH", "Onward! Papers and Essays", _) => StandardTalk()
	ConferenceEvent(_, _, _, _, "Online | SPLASH", "Onward! Essays and Papers", _) => StandardTalk()
	ConferenceEvent(_, _, _, _, "Online | SPLASH", "ECOOP 2020", _) => StandardTalk()
	ConferenceEvent(_, _, _, _, "Online | SPLASH", "Posters", _) => NotStreamed()
	othw => nothing
end


out = make_schedule(events, [by_track])
playlists = Dict([k=>schedule(k, v) for (k,v) in out])
timeline = make_timeline(playlists)
filled_timeline = fill_timeline(timeline, fillergen)
hs_timeline = highspeed_timeline(filled_timeline)
save_file(make_smil(hs_timeline), "schedule.smil")