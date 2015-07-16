$( document ).ready(function() {
    console.log( "ready!" );
    $( "#play" ).click(function() {
        data = {
            'username': $("#username").val(),
            'password': $("#password").val(),
            'team': $("#team").val(),
            'iterations': parseInt($("#iterations").val())
        }
        if($("#challengebutton").is(':checked') == true){
            data.challenge = $("#challengetext").val()
        }
        $.post("/api/play_game", data)
    });
});

