$(document).ready(function() {
    $('form').on('submit', function(event) {
        event.preventDefault();
        var text = $('#text').val();
        $.post('/convert', {text: text}, function(data) {
            $('#output').html(data);
        });
    });
});
