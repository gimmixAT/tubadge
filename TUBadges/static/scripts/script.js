$(function(){
    $('.badges').each(function(){
       $(this).isotope({
            itemClass : 'badge',
            animationEngine : 'jquery',
            resizable : false,
            layoutMode : 'masonry',
            masonry: { columnWidth: getColumnWidth() }
        });
    });
});

$(window).smartresize(function(){
    $('.badges').isotope({
        masonry: { columnWidth: getColumnWidth() }
    });
});

function getColumnWidth(){
    var w = window.innerWidth;
    var out = $('.badges').width() * 0.33;

    if(w < 600 ){
        out = $('.badges').width();
    } else if (w < 1100) {
        out = $('.badges').width() * 0.50;
    }

    console.log(w + ' -> ' + out);

    return out;
}