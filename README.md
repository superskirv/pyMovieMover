# pyMovieMover
About: This is designed to allow you to sequentially move large files from your download drive/folder to your storage drive/folder. The case use would be your torrent seed folder to your plex server.
<br><br>
 This is designed by default to place files in a sub-directories
 - Movies: based on the first letter of the title, ignoring "the" in the title name.
 - TV Shows: based on the file name, series name for first folder, and season for second sub folder.
 <br><br>
 There is a queuing system but its very far from perfect. You will have to delete partially moved files when it hangs or you terminate mid transfer, because it has a built in skip feature to avoid coping the same file twice. Im planning to incorporate a md5 hash check into it, but that makes it all run rather slow, and I need to update the UI to look nice. But if I did add that it would help inform your of bad transfers and could offer options to correct it.(future fixes)
 
