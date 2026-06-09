//# -*- coding: utf-8 -*-
//"""
//Created on Tue Apr 21 15:33:59 2026
//
//@author: j.thomas
//"""

function update_figures(){

    var nb_cases = parseInt(document.getElementById('nb_cases').value, 10);
    var nb_reviewers = parseInt(document.getElementById('nb_reviewers').value, 10);
    var nb_full = parseInt(document.getElementById('nb_full_reviewers').value, 10);
    var add_reviewers = parseInt(document.getElementById('expected_additional_reviewers').value, 10);
    var add_full = parseInt(document.getElementById('expected_additional_full_reviewers').value, 10);
    
    if (add_full > add_reviewers){
        add_full = add_reviewers;
        document.getElementById('expected_additional_full_reviewers').value = add_reviewers;
    }

    var total_rev = nb_reviewers + add_reviewers;
    var total_full = nb_full + add_full;
    
    document.getElementById('total_nb_reviewers').value = total_rev;
    document.getElementById('total_nb_full_reviewers').value = total_full;
    
    var reviewers_per_case = document.getElementById('nb_reviewers_per_case');
    var case_per_reviewer = document.getElementById('nb_cases_per_reviewer');
    
    if (document.getElementById('distribution_all').checked){
        case_per_reviewer.value = nb_cases;
    }
    
    if (document.getElementById('n_per_case').checked){
        var rev_per_case = document.getElementById('reviewers_per_case');
        var n = parseInt(rev_per_case.value, 10);
        if (n > total_rev){
            n = total_rev;
            rev_per_case.value = total_rev;
        }
        if (n < total_full){
            n = total_full;
            rev_per_case.value = total_full;
        }
        var value = Math.ceil((nb_cases * (n - total_full)) / (total_rev - total_full));
        console.log(value)
        case_per_reviewer.value = value;
    }
    
    if (document.getElementById('n_per_reviewer').checked){
        var n = parseInt(document.getElementById('cases_per_reviewer').value, 10);
        var value = Math.ceil(((total_rev - total_full) * n) / nb_cases) + total_full;
        reviewers_per_case.value = value;
    }
    
    if (document.getElementById('percent_per_reviewer').checked){
        var p = parseInt(document.getElementById('percentage').value, 10);
        var n = Math.ceil((p * nb_cases)/100);
        var value = Math.ceil(((total_rev - total_full) * n) / nb_cases) + total_full;
        reviewers_per_case.value = value;
    }

}

function update_everything(){
    if (document.getElementById('distribution_all').checked){
        var to_hide = ['select_n_per_case','select_n_per_reviewer','select_percent_per_reviewer', 'display_reviewers_per_case'];
        var to_show = ['display_cases_per_reviewer'];
    }
    if (document.getElementById('n_per_case').checked){
        var to_hide = ['select_n_per_reviewer','select_percent_per_reviewer', 'display_reviewers_per_case'];
        var to_show = ['select_n_per_case', 'display_cases_per_reviewer'];
    }
    if (document.getElementById('n_per_reviewer').checked){
        var to_hide = ['select_n_per_case','select_percent_per_reviewer', 'display_cases_per_reviewer'];
        var to_show = ['select_n_per_reviewer', 'display_reviewers_per_case'];
    }
    if (document.getElementById('percent_per_reviewer').checked){
        var to_hide = ['select_n_per_case','select_n_per_reviewer', 'display_cases_per_reviewer'];
        var to_show = ['select_percent_per_reviewer', 'display_reviewers_per_case'];
    }

    for (const hide of to_hide){
        var soonhidden = document.getElementById(hide);
        soonhidden.style.display = 'none';
    }
    
    for (const show of to_show){
        var soonshown = document.getElementById(show)
        soonshown.style.display = 'block';
    }
    update_figures();
}


window.addEventListener('load', update_everything);
