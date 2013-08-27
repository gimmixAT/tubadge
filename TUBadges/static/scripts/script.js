$(function(){
    $('.badges').each(function(){
       $(this).isotope({
            itemClass : 'badge',
            animationEngine : 'jquery',
            resizable : false,
            layoutMode : 'masonry',
            masonry: { columnWidth: getColumnWidth(1) }
        });
    });

    resizeFormElements($('.modal'));
});

$(window).smartresize(function(){
    $('.badges').isotope({
        masonry: { columnWidth: getColumnWidth(1) }
    });
});

function getColumnWidth(cols){
    var w = window.innerWidth;
    var out = $('.badges').width() * 1/(6*cols);

    if(w <= 280 ){
        out = $('.badges').width() * 1/cols;
    } else if(w <= 600 ){
        out = $('.badges').width() * 1/(2*cols);
    } else if (w <= 730) {
        out = $('.badges').width() * 1/(3*cols);
    } else if (w <= 1000) {
        out = $('.badges').width() * 1/(4*cols);
    } else if (w <= 1200) {
        out = $('.badges').width() * 1/(5*cols);
    }

    console.log(w + ' -> ' + out);

    return out;
}

function resizeFormElements(target){

    target.find('input.autosize').each(function(){
        var _this = this;
        var font = {
            'font-family' : $(this).css('font-family'),
            'font-weight' : $(this).css('font-weight'),
            'font-size' : $(this).css('font-size'),
            'line-height' : $(this).css('line-height'),
            'display' : 'block',
            'position' : 'absolute',
            'top' : 0,
            'white-space' : 'pre'
        }

        $(this).on('change input keydown keyup', function(e){
            var t = $('<div>'+ e.target.value+'</div>').css(font).appendTo('body');
            $(_this).css('width', t.width()+10);
            t.remove();
        }).change();
    });

    target.find('textarea.autosize').each(function(){
        var _this = this;
        var font = {
            'font-family' : $(this).css('font-family'),
            'font-weight' : $(this).css('font-weight'),
            'font-size' : $(this).css('font-size'),
            'line-height' : $(this).css('line-height'),
            'display' : 'block',
            'position' : 'absolute',
            'top' : 0,
            'width' : $(this).width()
        }
        console.log(font);
        $(this).on('change input keydown keyup', function(e){
            var t = $('<div class="pre">'+ e.target.value+'&nsbp;</div>').css(font).appendTo('body');
            $(_this).css('height', t.height()+11);
            //console.log(t.height());
            t.remove();
        }).change();
    });

}