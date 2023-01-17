function addEtiquette() {
    let texte = document.getElementById("input_etiquette").value;
    // Si etiquette vide, ne pas ajouter
    if (texte == "") { 
        return;
    }
    // Si etiquette déjà utilisée, ne pas ajouter
    document.getElementById("input_etiquette").value = "";
    let etiquettes_list = document.getElementsByClassName("etiquette");
    for (let etiquette of etiquettes_list) {
        if (etiquette.id == texte) {
            return; 
        }
    }
    // Ajouter etiquette
    let etiquettes = document.getElementById("etiquettes-list");
    let etiquette = document.createElement("div");
    etiquette.id = texte;
    etiquette.className = "etiquette";
    let etiquetteText = document.createElement("p");
    etiquetteText.innerHTML = texte;
    let etiquetteButton = document.createElement("button");
    etiquetteButton.type = "button";
    etiquetteButton.onclick = function() { delEtiquette(texte); };
    etiquetteButton.innerHTML = "Supprimer";
    etiquette.appendChild(etiquetteText);
    etiquette.appendChild(etiquetteButton);
    etiquettes.appendChild(etiquette);
    majInputEtiquettes()
}
function delEtiquette(id) {
    let etiquettes = document.getElementById("etiquettes-list");
    let etiquette = document.getElementById(id);
    etiquettes.removeChild(etiquette);
    majInputEtiquettes()
}
function majInputEtiquettes() {
    let etiquettes = document.getElementsByClassName("etiquette");
    let inputEtiquettes = document.getElementById("etiquettes");
    let liste = [];
    for (let etiquette of etiquettes) {
        liste.push(etiquette.id);
    }
    inputEtiquettes.value = JSON.stringify(liste);
}