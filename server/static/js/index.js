$( document ).ready(function() {
    $( "#playbutton" ).click(function() {
        data = {
            'username': $("#username").val(),
            'password': $("#password").val(),
            'teamfile': $("#teamfile").val(),
            'teamtext': $("#teamtext").val(),
            'browser': $("#browser").val(),
            'iterations': parseInt($("#iterations").val())
        }
        if($("#challengebutton").is(':checked') == true){
            data.challenge = $("#challengetext").val()
        }
        $.post("/api/play_game", data)
    });
});

