# KDrama Text Data

_w. jonas reger, abhi thanvi_

In this repository, a korean text corpus was collected, processed, and stored. Subtitle or caption documents were collected from Netflix, Viki, and OpenSubtitles. Subtitles were collected from 281 films or shows of the KDrama genre.

## Data

### Batch info (i.e., `raw/082022_batch_info.csv`)

The batch info dataset provides additional metadata on shows such as titles, genres, and links to additional data on IMDb.

Features:

- English (`string`) — Name of film/show in English.
- Korean (`string`) — Name of film/show in Korean.
- Other (`string`) — Name of film/show in English/Korean/Other.
- DL (`integer`) — If downloaded (0: no, 1: yes).
- ISSUE (`string`) — Notes of any issues with collection.
- CC SRC (`string`) — Origin of subtitle document (Netflix, Viki, OpenSubtitles).
- Validate (`integer`) — If validated (0: no, 1: yes, 2: yes but incomplete, 3: unknown).
- Assign (`string`) — Who is assigned to collect (Ignore).
- Genres (`string`) — List of genres of the show/film.
- List (`string`) — Collection list (Ignore).
- Link (`string`) — Info link for show/film.
- IMDb (`integer`) — If info link is an IMDb link (0: no, 1: yes).

### Processed Subtitles (i.e., `/data/subtitles/R---.csv`)

Each subtitle file was processed into a .csv version and stored in `/data`. Netflix, Viki, and OpenSubtitles typically had files in XML, VTT, and SRT, respectively.

Features:

- begin (`float`) — Time from start (seconds). Beginning of interval.
- end (`float`) — Time from start (seconds). Ending of interval.
- id (`string`) — Unique ID for item.
- text (`string`) — Original text.
- prep_verbal (`string`) — Pre-processed text for what viewers hear.
- prep_read (`string`) — Pre-processed text for what viewers read.

### Unique IDs

A unique ID is generated hierarchically as a string of 18 characters. Each section of an item ID points to a unique item at it's respective level. It is as shown below:

**Rxxx-Sxx-Txxx-Uxxxxxx**

The R, S, T, and U fields correspond to Show/Film, Season, Episode, and Line. The "Line" is the actual subtitle line shown when viewing a film with subtitles.

For example, the following ID matches to the first line of the first episode of the first season of the show with ID R000 (i.e., "100 Days My Prince").

**R000-S01-T001-U000001**

### Show/Film References (i.e., `data/show_ids.csv`, `data/show_info.csv`)

Features in `show_ids`:

- name (`string`) — Name of show/film.
- id (`string`) — Unique ID of show/film (i.e., R---)

Features in `show_info`:

- raw_src (`string`) — File path to a subtitle file in `/raw`.
- raw_name (`string`) — Name of folder containing all docs for a given show/film.
- raw_item_id (`string`) — Season and episode identifier within a show/film.
- file_type (`string`) — File type of subtitles document (i.e., xml, vtt, or srt).
- season (`integer`) — Season number of item.
- episode (`integer`) — Episode number of item.
- name (`string`) — Name of show/film.
- id (`string`) — Unique ID of show/film.
- item_id (`string`) — Unique ID of item (i.e., film or episode).









