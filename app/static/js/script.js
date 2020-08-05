$(document).ready(function(){
    $(".fa-heart").on('click', function(e){
        e.preventDefault();
        let question_id = $(this).data('id');
        let url = null
        if ($(this).hasClass('far')){
            $(this).removeClass('far')
            $(this).addClass('fas')
            url = "/like/"
        }
        else {
            $(this).removeClass('fas')
            $(this).addClass('far')
            url = "/unlike/"
        }
        
        $.get( url + question_id, function( data ) {
            $("#count-" + question_id).text(data['count'])
            $("#question-" + question_id + " a").each(function(){
                $(this).remove()
            })
            data['users'].forEach((el) => {
                $("#question-" + question_id).append(
                    `<a href="/user/${el['username']}">
                        <img class="user-image" src="${el['avatar']}">
                     </a>`
                )})
            data['users'].length > 0 ? display = "inline" : display = "none"
            $("#count-" + question_id).css("display", display)
            $("#liked-text-" + question_id).css("display", display)
        });
    })
})