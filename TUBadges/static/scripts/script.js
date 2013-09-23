
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

    $('.badge.preset').each(function(){
        setupBadgePreset($(this));
    });

    $('.badge:not(.preset)').each(function(){
        setupBadge($(this));
    });

    $('a[href="#add-preset"]').click(function(e){
        requestModal('/ajax/presetform', setupBadgePresetForm);
        return false;
    });
});

$(window).load(function(){
    $('.badges').isotope('reLayout');
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
function requestModal(url, maxWidth, callback){
    $.ajax({
        'url': url,
        'success': function(data){
            showModal(data, maxWidth, callback);
        },
        'dataType': 'html'
    });
}

/**
 * Displays the given HTML in a modal window
 */
function showModal(html, maxWidth, callback){
    if(typeof maxWidth === 'function') {
        callback = maxWidth;
        maxWidth = "";
    }
    $('.modal .contentbox').css('max-width', maxWidth).html(html).append('<a href="#close" class="close"></a>').parent().fadeIn();
    $('.modal .contentbox .close').click(function(){
        hideModal();
        return false;
    });
    if(callback && typeof callback === 'function'){
        callback($('.modal .contentbox'));
    }
}

/**
 * Hides the current modal window
 */
function hideModal(){
    $('.modal').fadeOut(function(){
        $('.contentbox', this).empty();
    });
}

function modalAlert(msg){
    alert(msg);
}

/**
 * Form related functions
 */

function setupForm(container){
    resizeFormElements(container);
    watchBadgeTypeChange(container);
}

/**
 * Badge Issue related funtions
 */
function setupBadgeForm(container){
    setupForm(container);

    container.find('#lva').each(function(){
        $(this).autocomplete({
            serviceUrl: $(this).data('serviceurl'),
            paramName: 'q',
            onSelect: function(d){
                $('#lva_id').val(d.data.id);
                $('#students').val(d.data.students);
            }
        });
    });

    container.find('#awardee').each(function(){
        var lastValue = '';
        $(this).change(function(){
            if($(this).val() != lastValue) {
                $('#awardee_id').val('');
            }
        }).autocomplete({
            serviceUrl: $(this).data('serviceurl'),
            paramName: 'q',
            onSelect: function(d){
                lastValue = d.value;
                $('#awardee_id').val(d.data);
            }
        });
    });

    container.find('#awarder').data('oldvalue', container.find('#awarder').val()).change(function(){
        if($(this).val() == $(this).data('oldvalue')){
            $('.opt.issuer').fadeOut();
        } else {
            $('.opt.issuer').fadeIn();
        }
    });

    container.find('input[type="button"].submit').click(function(e){
        e.preventDefault();

        var data = {
            'keywords': $('#keywords').val(),
            'comment': $('#comment').val(),
            'pid': $('#preset-id').val(),
            'rating': $('#rating').val()
        }

        container.find('.error').removeClass('error');

        var ok = true;

        if($('#awardee_id').val() != '') data['awardee_id'] = $('#awardee_id').val();
        else if ($('#awardee').val() != '') data['awardee'] = $('#awardee').val();
        else { $('#awardee').addClass('error'); ok = false; }

        if($('#lva_id').val() != '') data['lva_id'] = $('#lva_id').val();
        else if ($('#lva').val() != '') data['lva'] = $('#lva').val();
        else { $('#lva').addClass('error'); ok = false; }

        if($('#students').val() != '' || $('#students').val() > 0) data['students'] = $('#students').val();
        else { $('#students').addClass('error'); ok = false; }

        if($('#proof').val() != '') data['proof'] = $('#proof').val();
        else { $('#proof').addClass('error'); ok = false; }

        if($('#awarder').val() != $('#awarder').data('oldvalue')) data['awarder'] = $('#awarder').val();

        if(ok){
            $.ajax({
                'url': '/ajax/issue',
                'type': 'POST',
                'data': data,
                'success' : function(data){
                    if(!data.error){
                        hideModal();
                    } else {
                        modalAlert(data.msg);
                    }
                }
            });
        }
    });
}

function setupBadge(item){
    item.find('.active-area').click(function(e){
        requestModal('/ajax/badge?id='+$(this).parent().data('id'), 450);
        return false;
    });

    item.find('a[href="#toggle-public"]').click(function(e){
        var pid = $(this).parent().data('id');
        $(this).parent().toggleClass('public');
        $(this).attr('title', ($(this).parent().hasClass('public'))?'Veröffentlichung rückgängig machen':'Veröffentlichen');
        var _this = this;
        $.ajax({
            'url': '/ajax/togglepublic',
            'data': {
                'id' : pid
            },
            'type': 'POST',
            'success' : function(data){
                if(data.error){
                   $(_this).parent().toggleClass('public');
                   $(_this).attr('title', ($(this).parent().hasClass('public'))?'Veröffentlichung rückgängig machen':'Veröffentlichen')
                }
            }
        });
        return false;
    });

}


/**
 * Badge Preset related funtions
 */
function setupBadgePresetForm(container){

    setupForm(container);

    var badgePreview = $('.badgecreator .preview img', container);
    var parts = badgePreview.attr('src').split('?')[1].split('&');
    var po = {};
    for(var i=0; i<parts.length; i++){
        parts[i] = parts[i].split('=');
        po[parts[i][0]] = parts[i][1];
    }

    var currentShape, currentPattern, currentColor;
    if(po.s) currentShape = container.find('.shapes > li > a[data-name="'+po.s+'"]').addClass('selected').data('name');
    else currentShape = container.find('.shapes > li > a').first().addClass('selected').data('name');

    if(po.p) currentPattern = container.find('.patterns > li > a[data-name="'+po.p+'"]').addClass('selected').data('name');
    else currentPattern = container.find('.patterns > li > a').first().addClass('selected').data('name');

    if(po.c) currentColor = po.c;
    else currentColor = 'ffcc00';

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

    container.find('input[type="button"].submit').click(function(e){
        e.preventDefault();
        var pid = ($('#preset-id').val() != '')?$('#preset-id').val():null;
        $.ajax({
            'url': '/ajax/savepreset',
            'type': 'POST',
            'data': {
                'name': $('#name').val(),
                'img': badgePreview.attr('src'),
                'keywords': $('#keywords').val(),
                'id': pid
            },
            'success' : function(data){
                if(!data.error){
                    hideModal();
                    $.ajax({
                        'url': '/ajax/minpreset?id='+data.id,
                        'type': 'GET',
                        'success' : function(data){
                            if(pid){
                                $('.badges').isotope('remove', $('.badges .badge[data-id="'+pid+'"]'));
                            }
                            var item = $(data);
                            $('.badges').isotope( 'insert', item);
                            setupBadgePreset(item);
                        }
                    });
                } else {
                    modalAlert(data.msg);
                }
            }
        });
    });

    $("#shape-color").spectrum({
        color: currentColor,
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

    $('.slider', container).each(function(){
        setupSlider($(this));
    });
}

function setupBadgePreset(item){
    item.find('.active-area').click(function(e){
        requestModal('/ajax/preset?id='+$(this).parent().data('id'), 450);
        return false;
    });

    item.find('a[href="#issue"]').click(function(e){
        requestModal('/ajax/issueform?pid='+$(this).parent().parent().parent().data('id'), setupBadgeForm);
        return false;
    });

    item.find('a[href="#edit"]').click(function(e){
        requestModal('/ajax/presetform?id='+$(this).parent().parent().parent().data('id'), setupBadgePresetForm);
        return false;
    });

    item.find('a[href="#delete"]').click(function(e){
        var pid = $(this).parent().parent().parent().data('id');
        var item = $('.badges .badge[data-id="'+pid+'"]').clone();
        $('.badges').isotope('remove', $('.badges .badge[data-id="'+pid+'"]'));
        $.ajax({
            'url': '/ajax/deletepreset',
            'data': {
                'id' : pid
            },
            'type': 'POST',
            'success' : function(data){
                if(data.error){
                    $('.badges').isotope('insert', item);
                    setupBadgePreset(item);
                    modalAlert(data.msg);
                }
            }
        });
        return false;
    });

    item.find('a[href="#duplicate"]').click(function(e){
        $.ajax({
            'url': '/ajax/duplicatepreset',
            'type': 'POST',
            'data': {
                'id': $(this).parent().parent().parent().data('id')
            },
            'success' : function(data){
                if(!data.error){
                    $.ajax({
                        'url': '/ajax/minpreset?id='+data.id,
                        'type': 'GET',
                        'success' : function(data){
                            var item = $(data);
                            $('.badges').isotope( 'insert', item);
                            setupBadgePreset(item);
                        }
                    });
                } else {
                    modalAlert(data.msg);
                }
            }
        });
        return false;
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