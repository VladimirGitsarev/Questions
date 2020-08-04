$(document).ready(function(){
    $(".fa-heart").on('click', function(e){
        e.preventDefault()
        if ($(this).hasClass('far')){
            $(this).removeClass('far')
            $(this).addClass('fas')
        }
        else {
            $(this).removeClass('fas')
            $(this).addClass('far')
        }
        
    })
})