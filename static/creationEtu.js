
/*
Dropzone.options.myGreatDropzone = { 
  autoProcessQueue: false,
  paramName: "file", 
  maxFilesize: 2, 
  clickable: "#dropZone", // the ID of our parent wrapper div
  maxFiles: 1, // Limiter à un seul fichier
  acceptedFiles: ".csv", // Limiter aux fichiers CSV
  addRemoveLinks: true, // Ajouter un lien pour supprimer le fichier
  dictRemoveFile: "Supprimer", // Texte du lien de suppression
  dictInvalidFileType: "Seuls les fichiers CSV sont acceptés.", // Message d'erreur si le fichier n'est pas un CSV
  dictMaxFilesExceeded: "Un seul fichier est autorisé.", // Message d'erreur si on essaie d'uploader plus d'un fichier
  }



/*
const dropzone = document.getElementsByClassName("dropzone");

/*
dropzone.ondrop = (event) => {
  event.preventDefault();
  const files = event.dataTransfer.files;
  //console.log(files);
  dropzone.innerHTML = `${files.length} files dropped`;
  zone = document.getElementById("csv_file")
  zone.value = files;

};

dropzone.addEventListener("dragover", (event) => {
    event.preventDefault();
  });

  dropzone.addEventListener("drop", (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files;
    dropzone.innerHTML = `${file.length} file dropped`;
    zone = document.getElementById("dragDrop")
    zone.value = file;
  });

/*
const dropZone = document.getElementById("drop-zone");

// Handle dragover event
dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
});

// Handle drop event
dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  console.log("Files dropped: ", event.dataTransfer.files);
});



*/