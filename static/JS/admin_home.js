

function logout(){
    open ('/logout/', '_self')
}

function change_password(){
    open ('/change_password/', '_self')
}

function new_user(){
    open ('/new_user/', '_self')
}

function begin_study(){
    open ('/begin_study/', '_self')
}

function pause_study(){
    open ('/pause_study/', '_self')
}

function resume_study(){
    open ('/resume_study/', '_self')
}

function confirm_end(){
    open ('/confirm_end/', '_self')
}

function export_data(){
    open ('/export_data/', '_self')
}

function confirm_clear_users(){
    open ('/confirm_clear_users/', '_self')
}

function confirm_delete_user(userId){
    open ('/confirm_delete_user/' + userId, '_self')
}

function reset_password(userId){
    open ('/reset_password/' + userId, '_self')
}

