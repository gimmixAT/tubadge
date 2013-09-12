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
function requestModal(url, maxWidth){
    $.ajax({
        'url': url,
        'success': function(data){
            showModal(data, maxWidth);
        },
        'dataType': 'html'
    });
}

/**
 * Displays the given HTML in a modal window
 */
function showModal(html, maxWidth){
    $('.modal .contentbox').css('max-width', maxWidth).html(html).append('<a href="#close" class="close"></a>').fadeIn();
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


/**
 * Badge Preset Form related funtions
 */
function setupBadgePresetForm(container){
    var currentShape = container.find('.shapes > li > a').first().addClass('selected').data('name');
    var currentPattern = container.find('.patterns > li > a').first().addClass('selected').data('name');
    var currentColor = 'ffcc00'
    var badgePreview = $('.badgecreator .preview img', container);

    badgePreview.attr('src', '/svg?p='+currentPattern+'&s='+currentShape+'&c='+currentColor);

    $('a[href="#change-pattern"]', container).click(function(){
        currentPattern = $(this).data('name');
        $(this).parent().parent().find('a.selected').removeClass('selected');
        $(this).addClass('selected');
        badgePreview.attr('src', '/svg?p='+currentPattern+'&s='+currentShape+'&c='+currentColor);
        return false;
    });

    $('a[href="#change-shape"]', container).click(function(){
        currentShape = $(this).data('name');
        $(this).parent().parent().find('a.selected').removeClass('selected');
        $(this).addClass('selected');
        badgePreview.attr('src', '/svg?p='+currentPattern+'&s='+currentShape+'&c='+currentColor);
        return false;
    });

    $('input[type="button"].submit').click(function(e){
        e.preventDefault();
        $.ajax({
            'url': '/ajax/savepreset',
            'type': 'POST',
            'data': {
                'name': $('#name').val(),
                'img': badgePreview.attr('src'),
                'keywords': $('#keywords').val()
            }
        })
    });

    $("#shape-color").spectrum({
        color: '#ffcc00',
        localStorageKey: 'shapeColors',
        showPalette: true,
        showSelectionPalette: true,
        palette: ['#ffcc00', '#0070af'],
        showInitial: true,
        preferredFormat: 'hex',
        showInput: true,
        show: function(color) {
            var c = $("#shape-color").spectrum('container');
            var o = c.offset();
            c.css('left', (o.left-14)+'px').css('top', (o.top+5)+'px');
            return true;
        }, change : function(color){
            currentColor = color.toHexString().substr(1);
            badgePreview.attr('src', '/svg?p='+currentPattern+'&s='+currentShape+'&c='+currentColor);
        }
    });
}

/**
 *  csrf AJAX
 *  @author Django Team
 */
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            var csrftoken = $.cookie('csrftoken');
            if((!csrftoken || csrftoken == '') && $('input[name="csrfmiddlewaretoken"]').length >= 1) csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});