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
    watchBadgeTypeChange($('.modal'));

    $('.slider').each(function(){
        setupSlider($(this));
    });

    $('.autocomplete').each(function(){
        $(this).autocomplete({
            serviceUrl: $(this).data('serviceurl'),
            paramName: 'q'
        });
    });

    setupBadgePresetForm($('.modal .contentbox'));

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

        $(this).on('change input keydown keyup', function(e){
            var t = $('<div class="pre">'+ e.target.value+'&nsbp;</div>').css(font).appendTo('body');
            $(_this).css('height', t.height()+11);
            t.remove();
        }).change();
    });

}

function watchBadgeTypeChange(target){
    target.find('select').change(function(e){
        switch($(e.target).val()){
            case '0': target.find('.badge').removeClass('bronze silver gold').addClass('bronze'); break;
            case '2': target.find('.badge').removeClass('bronze silver gold').addClass('gold'); break;
            default: target.find('.badge').removeClass('bronze silver gold').addClass('silver'); break;
        }
    });
}

function setupSlider(target){
    var itemsPerPage = target.data('items_per_page');
    var next = $('#'+target.data('next'));
    var prev = $('#'+target.data('prev'));
    var pageIndicator = $('#'+target.data('pageindicator'));
    var pages = Math.ceil(target.children().length / itemsPerPage);
    var currentPage = 0;

    target.children().hide();

    slideToPage(target, -1, currentPage, itemsPerPage)

    pageIndicator.html(1+'/'+pages);

    next.click(function(){
        var oldPage = currentPage;
        currentPage++;
        if(currentPage > pages-1) currentPage = 0;
        pageIndicator.html((currentPage+1)+'/'+pages);
        slideToPage(target, oldPage, currentPage, itemsPerPage);
        return false;
    });

    prev.click(function(){
        var oldPage = currentPage;
        currentPage--;
        if(currentPage < 0) currentPage = pages-1;
        pageIndicator.html((currentPage+1)+'/'+pages);
        slideToPage(target, oldPage, currentPage, itemsPerPage);
        return false;
    });
}

function slideToPage(target, from, to, itemsPerPage){
    var children = target.children();

    if(from >= 0){
        var f = (from+1) * itemsPerPage;
        for(var c = f - itemsPerPage; c < f; c++){
            $(children[c]).hide();
        }
    }

    var t = (to+1) * itemsPerPage;
    for(var c = t - itemsPerPage; c < t; c++){
        $(children[c]).show();
    }
}

/**
 * Loads HTML via AJAX from the given url and calls showModal
 */
function requestModal(url){
    $.ajax({
        'url': url,
        'success': function(data){
            showModal(data);
        },
        'dataType': 'html'
    });
}

/**
 * Displays the given HTML in a modal window
 */
function showModal(html){
    $('.modal .contentbox').html(html).append('<a href="#close" class="close"></a>').fadeIn();
    $('.modal .contentbox .close').click(function(){
        hideModal();
        return false;
    });
}

/**
 * Hides the current modal window
 */
function hideModal(){
    $('.modal').fadeOut(function(){
        $('.contentbox', this).empty();
    });
}

function setupBadgePresetForm(container){
    var currentShape = '';
    var currentPattern = '';
    var badgePreview = $('.badgecreator .preview img', container);

    $('a[href="#change-pattern"]', container).click(function(){
        currentPattern = $(this).data('name');
        badgePreview.attr('src', '/svg?p='+currentPattern+'&s='+currentShape+'&c=ffcc00');
        return false;
    });

    $('a[href="#change-shape"]', container).click(function(){
        currentShape = $(this).data('name');
        badgePreview.attr('src', '/svg?p='+currentPattern+'&s='+currentShape+'&c=ffcc00');
        return false;
    });
}