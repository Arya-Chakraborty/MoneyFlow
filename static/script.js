function show_created_password(){
    var password = document.getElementById('created_password');
    if(password.type == "password"){
        password.type = "text";
    }
    else{
        password.type = "password"
    }
}
function show_confirmed_password(){
    var password = document.getElementById('confirm_password');
    if(password.type == "password"){
        password.type = "text";
    }
    else{
        password.type = "password"
    }
}