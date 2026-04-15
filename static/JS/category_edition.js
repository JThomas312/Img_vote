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
    console.log('il est passé par ici');
    console.log(name);
    console.log(cat_id);
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

function safeguard_prerequisite(event, elementId, cat_id){
    event.preventDefault();
    var name = document.getElementById(elementId).value;
    console.log('il est passé par ici');
    console.log(name);
    console.log(cat_id);
    url = '/safeguard_prerequisite?cat_id=' + cat_id + '&name=' + name;
    $.getJSON(url, function(data){}).then(() => { location.reload(); });
    return false;
}

function edit_prerequisite(event, pre_id, elementId, cat_id, action){
    event.preventDefault();
    var name = document.getElementById(elementId).value;
    url = '/edit_prerequisite?cat_id=' + cat_id + '&pre_id=' + pre_id + '&name=' + name + '&action=' + action;
    $.getJSON(url, function(data){});
    return false;
}

function safeguard_criterion(event, nameElementId, malignancyElementId, cat_id){
    console.log('il est passé par ici');
    event.preventDefault();
    var name = document.getElementById(nameElementId).value;
    var malignancy = document.getElementById(malignancyElementId).checked;
    url = '/safeguard_criterion?cat_id=' + cat_id + '&name=' + name + '&malignancy=' + malignancy;
    $.getJSON(url, function(data){}).then(() => { location.reload(); });
    return false;
}

function edit_criterion(event, crit_id, element, malignancyElement, cat_id, action){
    event.preventDefault();
    var name = element.value;
    var malignancy = malignancyElement.checked;
    url = '/edit_criterion?cat_id=' + cat_id + '&crit_id=' + crit_id + '&name=' + name + '&malignancy=' + malignancy + '&action=' + action;
    $.getJSON(url, function(data){});
    return false;
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
  newButton.addEventListener('click', function(event) {
    event.target.parentNode.remove();
  });
  
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
  
  var newSaveButton = document.createElement('button');
  newSaveButton.textContent = 'Save';
  newSaveButton.classList.add('saveCriterionButton');
  newSaveButton.addEventListener('click', function(event) {
    safeguard_criterion(event, newInput.id, newRadioYes.id, {{category.id}});
  });
  
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
  newButton.addEventListener('click', function(event) {
    event.target.parentNode.remove();
  });
  
  newprerequisiteWrapper.appendChild(newButton);

  var newSaveButton = document.createElement('button');
  newSaveButton.textContent = 'Save';
  newSaveButton.classList.add('savePrerequisiteButton');
  newSaveButton.addEventListener('click', function(event) {
    safeguard_prerequisite(event, newInput.id, {{category.id}});
  });
  
  newprerequisiteWrapper.appendChild(newSaveButton);

  prerequisiteContainer.appendChild(newprerequisiteWrapper);
});

