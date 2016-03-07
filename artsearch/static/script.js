$(document).ready(function(){
    $(".to_reveal").click(function(){
        $(this).next().toggle(500);
    });
});