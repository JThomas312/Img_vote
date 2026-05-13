
function remove_category(cat_id){
    url = '/remove_category?cat_id=' + cat_id;
    $.getJSON(url, function(data){});
    return false;
}

function remove_criterion(crit_id){
    url = '/remove_criterion?crit_id=' + crit_id;
    $.getJSON(url, function(data){});
    return false;
}
