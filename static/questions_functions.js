function addAnswer() {
    answers = document.getElementById("answers");
    answer = document.createElement("div");
    answer.id = "answer" + nbAnswers;
    answerCheckbox = document.createElement("input");
    answerCheckbox.type = "checkbox";
    answerCheckbox.name = "correct" + nbAnswers;
    answerCheckbox.value = "1";
    answerText = document.createElement("input");
    answerText.type = "text";
    answerText.name = "text" + nbAnswers;
    answerText.placeholder = "Réponse " + (nbAnswers + 1);
    answerDelete = document.createElement("button");
    answerDelete.type = "button";
    answerDelete.className = "btn btn-labeled btn-danger";
    answerDelete.addEventListener("click", delAnswer);
    answerDeleteSpan = document.createElement("span");
    answerDeleteSpan.className = "btn-label";
    answerDeleteSpan_i = document.createElement("i");
    answerDeleteSpan_i.className = "fa fa-trash"

    answerDeleteSpan.appendChild(answerDeleteSpan_i)
    answerDelete.appendChild(answerDeleteSpan);
    answer.appendChild(answerCheckbox);
    answer.appendChild(answerText);
    answer.appendChild(answerDelete);
    
    answers.appendChild(answer);
    
    nbAnswers++;
    nbAnswersInput = document.getElementById("nbAnswers");
    nbAnswersInput.value = nbAnswers;
}
function delAnswer() {
    answer = document.getElementById("answer" + (nbAnswers - 1));
    answers.removeChild(answer);
    nbAnswers--;
    nbAnswersInput = document.getElementById("nbAnswers");
    nbAnswersInput.value = nbAnswers;
}

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
    let etiquetteButton = document.createElement("button");
    etiquetteButton.type = "button";
    etiquetteButton.className = "btn btn-primary btn-sm";
    etiquetteButton.data_bs_toggle = "tooltip";
    etiquetteButton.data_bs_placement = "top";
    etiquetteButton.title = "appuyez pour supprimer";
    etiquetteButton.onclick = function() { delEtiquette(texte); };
    etiquetteButton.innerHTML = texte;
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