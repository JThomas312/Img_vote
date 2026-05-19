//# -*- coding: utf-8 -*-
//"""
//Created on Fri Apr 10 17:02:03 2026
//
//@author: j.thomas
//"""


function updateMalignancyVisibility(show){
    var blocks = document.getElementsByClassName( 'criterionMalignancy' );
    for (let i = 0; i < blocks.length; i++){
        if (show) {
            blocks[i].style.display='block';
        }
        else {
            blocks[i].style.display='none';
            var uncheck_yes = blocks[i].querySelector('[id$="_yes"]');
            uncheck_yes.checked=false
            var uncheck_no = blocks[i].querySelector('[id$="_no"]');
            uncheck_no.checked=false
        }
    }
}

function updateMalignancy(show){
    var malignancyDiv = document.getElementById('malignancy_choice')
    var malignancy_yes = document.getElementById('malignancy_yes')
    var malignancy_no= document.getElementById('malignancy_no')
    if (show){
        malignancyDiv.style.display='block';
    }
    else{
        malignancyDiv.style.display='none';
        malignancy_yes.checked = false;
        malignancy_no.checked = true;
        updateMalignancyVisibility(show);
    }
}

function updateOptional(show){
    var optionalDiv = document.getElementById('PrerequisitesVisibility')
    if (show){
        optionalDiv.style.display='block';
    }
    else{
        optionalDiv.style.display='none';
    }
}

function initMalignancy(){
     var display = document.getElementById('gold_standard_yes').checked
     updateMalignancy(display);
}

function initMalignancyVisibility(){
     var display = document.getElementById('malignancy_yes').checked
     updateMalignancyVisibility(display);
}

function initOptional(){
     var display = document.getElementById('optional_yes').checked
     updateOptional(display);
}

window.addEventListener('load', initMalignancy);
window.addEventListener('load', initMalignancyVisibility);
window.addEventListener('load', initOptional);


function safeguard_name(event, cat_id){
    event.preventDefault();
    var name = document.getElementById("category_name").value;
    url = '/safeguard_category?cat_id=' + cat_id + '&value=' + name + '&field=name';
    $.getJSON(url, function(data){});
    return false;
}

function safeguard_trust(cat_id, value){
    url = '/safeguard_category?cat_id=' + cat_id + '&value=' + value + '&field=trust';
    $.getJSON(url, function(data){});
    return false;
}

function safeguard_type(cat_id, value){
    url = '/safeguard_category?cat_id=' + cat_id + '&value=' + value + '&field=type';
    $.getJSON(url, function(data){});
    return false;
}

function safeguard_tutorial(cat_id, value){
    url = '/safeguard_category?cat_id=' + cat_id + '&value=' + value + '&field=tutorial';
    $.getJSON(url, function(data){});
    return false;
}

function safeguard_na(cat_id, value){
    url = '/safeguard_category?cat_id=' + cat_id + '&value=' + value + '&field=na';
    $.getJSON(url, function(data){});
    return false;
}

function safeguard_optional(cat_id, value){
    url = '/safeguard_category?cat_id=' + cat_id + '&value=' + value + '&field=optional';
    $.getJSON(url, function(data){});
    return false;
}

function safeguard_gold_standard(cat_id, value){
    if (value == false){
        var malignancy_yes = document.getElementById('malignancy_yes')
        malignancy_yes.checked = false
        var malignancy_no = document.getElementById('malignancy_no')
        malignancy_no.checked = true
        safeguard_malignancy(cat_id, 'false')
    }
    url = '/safeguard_category?cat_id=' + cat_id + '&value=' + value + '&field=gold_standard';
    $.getJSON(url, function(data){});
    return false;
}

function safeguard_malignancy(cat_id, value){
    url = '/safeguard_category?cat_id=' + cat_id + '&value=' + value + '&field=malignancy';
    $.getJSON(url, function(data){});
    return false;
}
 
function safeguard_prerequisite(event, nameElement, cat_id){
    event.preventDefault();
    var nameElementId = nameElement.id;
    var name = document.getElementById(nameElementId).value;
    url = '/safeguard_prerequisite?cat_id=' + cat_id + '&name=' + name;
    $.getJSON(url, function(data){
        
        var newId = data.result;
        if (newId == null){
            nameElement.parentNode.remove();
        }
        else{
            var category_id = document.getElementById('category_id').value;
            var num = nameElementId.slice(17);
            
            var removeButton = document.getElementById('removePrerequisiteButton' + num);
            var saveButton = document.getElementById('savePrerequisiteButton' + num);
            
            removeButton.setAttribute('onclick', 'edit_prerequisite(event, ' + newId + ', "prerequisiteField' + num + '", ' + category_id + ', "remove")')
            
            saveButton.setAttribute('onclick', 'edit_prerequisite(event, ' + newId + ', "prerequisiteField' + num + '", ' + category_id + ', "edit")');
            
            nameElement.classList.add('saved')
        }
    });
    return false;
}

function edit_prerequisite(event, pre_id, element, cat_id, action){
    event.preventDefault();
    var name = element.value;
    if (name == undefined){
        name = document.getElementById(element).value;
    }
    url = '/edit_prerequisite?cat_id=' + cat_id + '&pre_id=' + pre_id + '&name=' + name + '&action=' + action;
    $.getJSON(url, function(data){});
    if (action == 'remove'){
        event.target.parentNode.remove();
    }
    return false;
}

function safeguard_criterion(event, nameElement, malignancyYesElement, malignancyNoElement, cat_id){
    event.preventDefault();
    var nameElementId = nameElement.id;
    var malignancyYesElementId = malignancyYesElement.id;
    var malignancyNoElementId = malignancyNoElement.id;
    var name = document.getElementById(nameElementId).value;
    var malignancy = document.getElementById(malignancyYesElementId).checked;
    url = '/safeguard_criterion?cat_id=' + cat_id + '&name=' + name + '&malignancy=' + malignancy;
    $.getJSON(url, function(data){
    
        var newId = data.result;
        if (newId == null){
            nameElement.parentNode.remove();
        }
        else{
            var category_id = document.getElementById('category_id').value;
            var num = nameElementId.slice(14);
    
            var removeButton = document.getElementById('removeCriterionButton' + num);
            var saveButton = document.getElementById('saveCriterionButton' + num);
            var malYes = document.getElementById(malignancyYesElementId);
            var malNo = document.getElementById(malignancyNoElementId);
            
            removeButton.setAttribute('onclick', 'edit_criterion(event, ' + newId + ', "criterionField' + num + '", "criterionMalignancy' + num + '_yes", ' + category_id + ', "remove")');
            
            saveButton.setAttribute('onclick', 'edit_criterion(event, ' + newId + ', "criterionField' + num + '", "criterionMalignancy' + num + '_yes", ' + category_id + ', "edit")');
            
            malYes.setAttribute('onclick', 'safeguard_criterion_malignancy(' + newId + ', true)');
            
            malNo.setAttribute('onclick', 'safeguard_criterion_malignancy(' + newId + ', false)');
            
            nameElement.classList.add('saved')
        }
    });
    return false;
}

function edit_criterion(event, crit_id, element, malignancyElement, cat_id, action){
    event.preventDefault();
    var name = element.value;
    if (name == undefined){
        name = document.getElementById(element).value;
    }
    var malignancy = malignancyElement.checked;
    if (malignancy == undefined){
        malignancy = document.getElementById(malignancyElement).checked;
    }
    url = '/edit_criterion?cat_id=' + cat_id + '&crit_id=' + crit_id + '&name=' + name + '&malignancy=' + malignancy + '&action=' + action;
    $.getJSON(url, function(data){});
    if (action == 'remove'){
        event.target.parentNode.remove();
    }
    return false;
}

function safeguard_criterion_malignancy(crit_id, malignancy){
    url = '/safeguard_criterion_malignancy?crit_id=' + crit_id + '&malignancy=' + malignancy
    $.getJSON(url, function(data){});
    return false;
}
 
function updateNA(category, show){
    var na_div = document.getElementById('na_visibility');
    var na_yes = document.getElementById('na_yes');
    var na_no = document.getElementById('na_no');
    if (show){
        na_div.style.display='block';
    }
    else{
        na_div.style.display='none';
        na_yes.checked = false;
        na_no.checked = true;
        safeguard_na(category, show);
    }
}

function updateGoldStandard(category, show){
    var gold_standard_allowed = document.getElementById('gold_standard_allowed').value;
    if (gold_standard_allowed == 'True'){
        var gold_standard_div = document.getElementById('gold_standard_visibility');
        var gold_standard_yes = document.getElementById('gold_standard_yes');
        var gold_standard_no = document.getElementById('gold_standard_no');
        if (show){
            gold_standard_div.style.display='block';
        }
        else{
            gold_standard_div.style.display='none';
            gold_standard_yes.checked = false;
            gold_standard_no.checked = true;
            safeguard_gold_standard(category, show)
        }
    }
}

function initNA(){
     var display = document.getElementById('criteria').checked || document.getElementById('one_of').checked;
     var category_id = document.getElementById('category_id').value;
     updateNA(category_id, display);
}

function initGoldStandard(){
     var display = document.getElementById('one_of').checked;
     var category_id = document.getElementById('category_id').value;
     updateGoldStandard(category_id, display);
}

window.addEventListener('load', initNA);
window.addEventListener('load', initGoldStandard);

function removeParent(event){
    event.target.parentNode.remove();
}

document.getElementById('addCriterionButton').addEventListener('click', function(event) {
  event.preventDefault();

  var criteriaContainer = document.getElementById('criteriaContainer');
  var newcriterionWrapper = document.createElement('div');
  newcriterionWrapper.classList.add('criterionWrapper');

  var newInput = document.createElement('input');
  newInput.type = 'text';
  newInput.id = 'criterionField' + (criteriaContainer.children.length + 1);
  newInput.name = 'criterionField' + (criteriaContainer.children.length + 1);
  
  newcriterionWrapper.appendChild(newInput);

  var newButton = document.createElement('button');
  newButton.textContent = 'Remove';
  newButton.classList.add('removeCriterionButton');
  newButton.id = 'removeCriterionButton' + (criteriaContainer.children.length + 1);
  newButton.setAttribute('onclick', 'removeParent(event)');
  
  newcriterionWrapper.appendChild(newButton);
  
  var display = document.getElementById('malignancy_yes').checked

  var newDiv = document.createElement('div');
  newDiv.className = 'criterionMalignancy';
  newDiv.id = 'criterionMalignancy' + (criteriaContainer.children.length + 1);
  if (display){
      newDiv.style.display='block'
  }
  else{
      newDiv.style.display='none'
  }
  
  var newRadioYes = document.createElement('input');
  newRadioYes.type = 'radio';
  newRadioYes.id = 'criterionMalignancy' + (criteriaContainer.children.length + 1) + '_yes';
  newRadioYes.name = 'criterionMalignancy' + (criteriaContainer.children.length + 1);
  newRadioYes.value = 1;
  
  var newLabelYes = document.createElement('label');
  newRadioYes.htmlFor = 'criterionMalignancy' + (criteriaContainer.children.length + 1);
  newLabelYes.innerHTML = 'Malignant';
  
  var newRadioNo = document.createElement('input');
  newRadioNo.type = 'radio';
  newRadioNo.id = 'criterionMalignancy' + (criteriaContainer.children.length + 1) + '_no';
  newRadioNo.name = 'criterionMalignancy' + (criteriaContainer.children.length + 1);
  newRadioNo.value = 0;
  
  var newLabelNo = document.createElement('label');
  newRadioNo.htmlFor = 'criterionMalignancy' + (criteriaContainer.children.length + 1);
  newLabelNo.innerHTML = 'Begnin';
  
  var category_id = document.getElementById('category_id').value;
  
  var newSaveButton = document.createElement('button');
  newSaveButton.textContent = 'Save';
  newSaveButton.classList.add('saveCriterionButton');
  newSaveButton.id = 'saveCriterionButton' + (criteriaContainer.children.length + 1);
  newSaveButton.setAttribute('onclick', 'safeguard_criterion(event, ' + newInput.id + ', ' + newRadioYes.id + ', ' + newRadioNo.id + ', ' + category_id + ')');
  
  newcriterionWrapper.appendChild(newSaveButton);
  
  newcriterionWrapper.appendChild(newDiv);
  newDiv.appendChild(newRadioYes);
  newDiv.appendChild(newLabelYes);
  newDiv.appendChild(newRadioNo);
  newDiv.appendChild(newLabelNo);

  criteriaContainer.appendChild(newcriterionWrapper);
});

document.getElementById('addPrerequisiteButton').addEventListener('click', function(event) {
  event.preventDefault();

  var prerequisiteContainer = document.getElementById('prerequisiteContainer');
  var newprerequisiteWrapper = document.createElement('div');
  newprerequisiteWrapper.classList.add('prerequisiteWrapper');

  var newInput = document.createElement('input');
  newInput.type = 'text';
  newInput.id = 'prerequisiteField' + (prerequisiteContainer.children.length + 1);
  newInput.name = 'prerequisiteField' + (prerequisiteContainer.children.length + 1);
  newprerequisiteWrapper.appendChild(newInput);

  var newButton = document.createElement('button');
  newButton.textContent = 'Remove';
  newButton.classList.add('removePrerequisiteButton');
  newButton.id = 'removePrerequisiteButton' + (prerequisiteContainer.children.length + 1);
  newButton.setAttribute('onclick', 'removeParent(event)');
  
  newprerequisiteWrapper.appendChild(newButton);

  var category_id = document.getElementById('category_id').value;

  var newSaveButton = document.createElement('button');
  newSaveButton.textContent = 'Save';
  newSaveButton.classList.add('savePrerequisiteButton');
  newSaveButton.id = 'savePrerequisiteButton' + (prerequisiteContainer.children.length + 1);
  newSaveButton.setAttribute('onclick', 'safeguard_prerequisite(event, ' + newInput.id + ', ' + category_id + ')');
  
  newprerequisiteWrapper.appendChild(newSaveButton);

  prerequisiteContainer.appendChild(newprerequisiteWrapper);
});

