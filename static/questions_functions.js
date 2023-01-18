function addAnswer(text = "", isCorrect = false) {
    // Nouvelle réponse
    let new_answer = document.createElement("div");
    new_answer.className = "answer";
    // Checkbox
    let answerCheckbox = document.createElement("input");
    answerCheckbox.type = "checkbox";
    answerCheckbox.name = "correct";
    answerCheckbox.className = "isCorrect";
    answerCheckbox.value = isCorrect.toString();
    answerCheckbox.checked = isCorrect;
    answerCheckbox.onclick = function() {
        if (answerCheckbox.checked) {
            answerCheckbox.value = "true";
        } else {
            answerCheckbox.value = "false";
        }
    };
    // Champ de texte
    let answerText = document.createElement("input");
    answerText.type = "text";
    answerText.name = "answer_text";
    answerText.placeholder = "Réponse";
    answerText.value = text;
    // Bouton supprimer
    let answerDelete = document.createElement("button");
    answerDelete.type = "button";
    answerDelete.className = "btn btn-labeled btn-danger";
    answerDelete.onclick = function() {
        new_answer.remove();
    };
    answerDeleteSpan = document.createElement("span");
    answerDeleteSpan.className = "btn-label";
    answerDeleteSpan_i = document.createElement("i");
    answerDeleteSpan_i.className = "fa fa-trash"
    answerDeleteSpan.appendChild(answerDeleteSpan_i)
    answerDelete.appendChild(answerDeleteSpan);
    // Ajout à la réponse des champs
    new_answer.appendChild(answerCheckbox);
    new_answer.appendChild(answerText);
    new_answer.appendChild(answerDelete);
    
    let answers = document.getElementById("answers");
    answers.appendChild(new_answer);
}
function majAnswers() {
    let answers = [];
    let answers_list = document.getElementsByClassName("answer");
    for (let answer of answers_list) {
        let answer_text = answer.children[1].value;
        let answer_correct = answer.children[0].value;
        answers.push({
            "text": answer_text,
            "isCorrect": answer_correct
        });
    }
    let answers_json = document.getElementById("answers_json");
    answers_json.value = JSON.stringify(answers);
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
    majInputEtiquettes();
};
function majInputEtiquettes() {
    let etiquettes = document.getElementsByClassName("etiquette");
    let inputEtiquettes = document.getElementById("etiquettes");
    let liste = [];
    for (let etiquette of etiquettes) {
        liste.push(etiquette.id);
    }
    inputEtiquettes.value = JSON.stringify(liste);
}