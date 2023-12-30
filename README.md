# pyMovieMover
About: This is designed to allow you to sequentially move large files from your download drive/folder to your storage drive/folder. The use case would be your torrent seed folder to your plex server.
<br><br>
 This is designed by default to place files in a sub-directories
 - Movies:
   - EX: The.Cool.Movie.1999.other.stuff.avi
     - Places file in -> C:\storage\movies\C\The.Cool.Movie.1999.other.stuff.avi
   - The user destination string must end with the word "movies"
     - EX: 'C:\storage\movies'
   - Places files in folders based on the first letter of the title, ignoring "the" in the title name.
 - TV Shows:
   - EX: This.Cool.Show.S02E03.Random.Title.or.Other.Stuff.mkv
     - Places file in -> C:\storage\shows\This Cool Show\Season 02\This.Cool.Show.S02E03.Random.Title.or.Other.Stuff.mkv
   - The user destination string must end with the word "shows" or "anime"
     - EX: 'C:\storage\shows' or 'C:\storage\anime'
   - Places files in folders based on the file name
     - Series name for first folder
     - Season XX for second sub folder.
 - Blacklist:
    - This is a custom list to avoid certain files. By default it will skip a few sample video files. But the black list supports regexp type entries if you want to get more complicated. Im just lazy, so I am just adding exact file names as I come across them.
 - ISSUES: If the file name doesnt meet the exacting requiremnts, it will have issues. Please review the destination before coping file.
 <br><br>
 There is a queuing system but its very far from perfect. You may have to delete partially moved files when it hangs or you terminate mid transfer. It has a built in skip feature to avoid copying the same file twice and will overwrite files of different sizes. Im planning to incorporate a md5 hash check into it, but that makes it all run rather slow. Mostly I need a better/more ways to figure out movie titles/season names/season numbers.
