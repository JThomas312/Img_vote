//# -*- coding: utf-8 -*-
//"""
//Created on Fri Apr 10 17:02:03 2026
//
//@author: j.thomas
//"""

function debounce(fn, delay) {
    var timer;
    return function() {
        var args = arguments;
        var ctx = this;
        clearTimeout(timer);
        timer = setTimeout(function() { fn.apply(ctx, args); }, delay);
    };
}

function attachCriterionAutoSave(input, getCritId, catId) {
    var handler = debounce(function() {
        var critId = getCritId();
        var wrapper = input.parentNode;
        var malYes = wrapper.querySelector('[id$="_yes"][type="radio"]');
        var malNo  = wrapper.querySelector('[id$="_no"][type="radio"]');
        var name = input.value;
        var malignancy = malYes ? malYes.checked : false;
        if (!critId) {
            if (!name.trim()) return;
            // No DB id yet — trigger first-save via safeguard_criterion
            var url = '/safeguard_criterion?cat_id=' + catId + '&name=' + encodeURIComponent(name) + '&malignancy=' + malignancy;
            $.getJSON(url, function(data) {
                var newId = data.result;
                if (newId == null) {
                    wrapper.remove();
                } else {
                    input.dataset.critId = newId;
                    if (malYes) malYes.setAttribute('onclick', 'safeguard_criterion_malignancy(' + newId + ', true)');
                    if (malNo)  malNo.setAttribute('onclick',  'safeguard_criterion_malignancy(' + newId + ', false)');
                    var removeBtn = wrapper.querySelector('.removeCriterionButton');
                    if (removeBtn) {
                        var num = input.id.slice(14);
                        removeBtn.setAttribute('onclick', 'edit_criterion(event, ' + newId + ', "criterionField' + num + '", "criterionMalignancy' + num + '_yes", ' + catId + ', "remove")');
                    }
                    input.classList.add('saved');
                }
            });
        } else {
            // Already has a DB id — use edit_criterion
            var url = '/edit_criterion?cat_id=' + catId + '&crit_id=' + critId + '&name=' + encodeURIComponent(name) + '&malignancy=' + malignancy + '&action=edit';
            $.getJSON(url, function() {});
        }
    }, 800);
    input.addEventListener('input', handler);
}
function setPrerequisiteError(input, message) {
    input.classList.add('border-red-500');
    input.classList.remove('saved');
    input.title = message;
}

function clearPrerequisiteError(input) {
    input.classList.remove('border-red-500');
    input.title = '';
}

function attachPrerequisiteAutoSave(input, getPreId, catId) {
    var handler = debounce(function() {
        var preId = getPreId();
        var name = input.value;
        clearPrerequisiteError(input);
        if (!preId) {
            if (!name.trim()) return;
            var url = '/safeguard_prerequisite?cat_id=' + catId + '&name=' + encodeURIComponent(name);
            $.getJSON(url, function(data) {
                var newId = data.result;
                if (newId == null) {
                    setPrerequisiteError(input, 'No matching answer found. The name must exactly match an existing answer from another category.');
                } else {
                    input.dataset.preId = newId;
                    var removeBtn = input.parentNode.querySelector('.removePrerequisiteButton');
                    if (removeBtn) {
                        var num = input.id.slice(17);
                        removeBtn.setAttribute('onclick', 'edit_prerequisite(event, ' + newId + ', prerequisiteField' + num + ', ' + catId + ', "remove")');
                    }
                    input.classList.add('saved');
                }
            });
        } else {
            $.getJSON('/edit_prerequisite?cat_id=' + catId + '&pre_id=' + preId + '&name=' + encodeURIComponent(name) + '&action=edit', function(data) {
                if (data.result != null) {
                    input.dataset.preId = data.result;
                } else {
                    setPrerequisiteError(input, 'No matching answer found. The name must exactly match an existing answer from another category.');
                }
            });
        }
    }, 800);
    input.addEventListener('input', function() {
        clearPrerequisiteError(input);
        handler.apply(this, arguments);
    });
}


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

window.addEventListener('load', function() {
    var catId = document.getElementById('category_id').value;

    // Auto-save for category name
    var nameInput = document.getElementById('category_name');
    var debouncedSaveName = debounce(function() {
        $.getJSON('/safeguard_category?cat_id=' + catId + '&value=' + encodeURIComponent(nameInput.value) + '&field=name');
    }, 800);
    nameInput.addEventListener('input', debouncedSaveName);

    // Auto-save for existing criteria inputs
    var criteriaContainer = document.getElementById('criteriaContainer');
    criteriaContainer.querySelectorAll('input[data-crit-id]').forEach(function(input) {
        attachCriterionAutoSave(input, function() { return input.dataset.critId; }, catId);
    });

    // Auto-save for existing prerequisite inputs
    var prerequisiteContainer = document.getElementById('prerequisiteContainer');
    if (prerequisiteContainer) {
        prerequisiteContainer.querySelectorAll('input[data-pre-id]').forEach(function(input) {
            attachPrerequisiteAutoSave(input, function() { return input.dataset.preId; }, catId);
        });
    }
});


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
            safeguard_gold_standard(category, show);
            updateMalignancy(show);
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
  newcriterionWrapper.className = 'criterionWrapper flex items-center gap-2 bg-white rounded-xl border border-slate-200 px-3 py-2 shadow-sm';

  var newInput = document.createElement('input');
  newInput.type = 'text';
  newInput.id = 'criterionField' + (criteriaContainer.children.length + 1);
  newInput.name = 'criterionField' + (criteriaContainer.children.length + 1);
  newInput.className = 'flex-1 border border-slate-200 rounded-lg px-2 py-1.5 text-sm bg-slate-50';

  newcriterionWrapper.appendChild(newInput);

  var newButton = document.createElement('button');
  newButton.textContent = '✕';
  newButton.className = 'removeCriterionButton text-danger text-xs px-2.5 py-1 rounded-lg border border-red-200 hover:bg-red-50 font-medium';
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

  var newInnerDiv = document.createElement('div');
  newInnerDiv.className = 'flex gap-2 text-xs mt-1';

  var newRadioYes = document.createElement('input');
  newRadioYes.type = 'radio';
  newRadioYes.id = 'criterionMalignancy' + (criteriaContainer.children.length + 1) + '_yes';
  newRadioYes.name = 'criterionMalignancy' + (criteriaContainer.children.length + 1);
  newRadioYes.value = 1;
  newRadioYes.className = 'accent-rose-600';

  var newLabelYes = document.createElement('label');
  newLabelYes.htmlFor = newRadioYes.id;
  newLabelYes.className = 'flex items-center gap-1 cursor-pointer';
  newLabelYes.appendChild(newRadioYes);
  newLabelYes.appendChild(document.createTextNode(' Malignant'));

  var newRadioNo = document.createElement('input');
  newRadioNo.type = 'radio';
  newRadioNo.id = 'criterionMalignancy' + (criteriaContainer.children.length + 1) + '_no';
  newRadioNo.name = 'criterionMalignancy' + (criteriaContainer.children.length + 1);
  newRadioNo.value = 0;
  newRadioNo.className = 'accent-green-600';

  var newLabelNo = document.createElement('label');
  newLabelNo.htmlFor = newRadioNo.id;
  newLabelNo.className = 'flex items-center gap-1 cursor-pointer';
  newLabelNo.appendChild(newRadioNo);
  newLabelNo.appendChild(document.createTextNode(' Benign'));

  var category_id = document.getElementById('category_id').value;

  newcriterionWrapper.appendChild(newDiv);
  newDiv.appendChild(newInnerDiv);
  newInnerDiv.appendChild(newLabelYes);
  newInnerDiv.appendChild(newLabelNo);

  criteriaContainer.appendChild(newcriterionWrapper);

  // Wire up debounced auto-save for this new criterion (no DB id yet)
  attachCriterionAutoSave(newInput, function() { return newInput.dataset.critId || null; }, category_id);
});

document.getElementById('addPrerequisiteButton').addEventListener('click', function(event) {
  event.preventDefault();

  var prerequisiteContainer = document.getElementById('prerequisiteContainer');
  var newprerequisiteWrapper = document.createElement('div');
  newprerequisiteWrapper.className = 'prerequisiteWrapper flex items-center gap-2 bg-indigo-50 rounded-xl px-3 py-2';

  var newInput = document.createElement('input');
  newInput.type = 'text';
  newInput.id = 'prerequisiteField' + (prerequisiteContainer.children.length + 1);
  newInput.name = 'prerequisiteField' + (prerequisiteContainer.children.length + 1);
  newInput.className = 'flex-1 border border-slate-200 rounded-lg px-2 py-1.5 text-sm bg-white';
  newprerequisiteWrapper.appendChild(newInput);

  var newButton = document.createElement('button');
  newButton.textContent = 'Remove';
  newButton.className = 'removePrerequisiteButton text-danger text-xs px-3 py-1 rounded-lg border border-red-200 hover:bg-red-50 font-medium';
  newButton.id = 'removePrerequisiteButton' + (prerequisiteContainer.children.length + 1);
  newButton.setAttribute('onclick', 'removeParent(event)');
  newprerequisiteWrapper.appendChild(newButton);

  prerequisiteContainer.appendChild(newprerequisiteWrapper);

  var category_id = document.getElementById('category_id').value;
  attachPrerequisiteAutoSave(newInput, function() { return newInput.dataset.preId || null; }, category_id);
});

