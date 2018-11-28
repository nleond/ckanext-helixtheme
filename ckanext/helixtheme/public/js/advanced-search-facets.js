jQuery(document).ready(function ($, _) {

    var console = window.console
    var debug = $.proxy(console, 'debug')

    handleFacets();
});

var LIMIT = 4;

function handleFacets() {

    // Initially hide facet items with index over LIMIT
    function init_hide() {
        var cat_list = $('.fields .switches');
        cat_list.each(function (index) {
            $(this).addClass('li-hidden');

            var list = $(this).find('label');
            list.each(function (index) {
                if (index >= LIMIT) {
                    $(this).css("display", "none");
                }
                console.log($(this));
                //if (index == LIMIT) {
                //    $(this).addClass("no-bottom-border");
                //}
                //checkboxes =  $(this).find('input');
                //texts = $(this).find('a');
            });
            
        });
        // turn to uppercase and remove greek intonation 
        var list2 = $('.upper');
        list2.each(function (index) {
            console.log($(this).text())
            $(this).text().toUpperCase().replace(/Ά/g, 'Α').replace(/Έ/g, 'Ε').replace(/Ή/g, 'Η').replace(/Ί/g, 'Ι').replace( /Ό/g, 'Ο').replace(/Ύ/g, 'Υ').replace(/Ώ/g, 'Ω');
        });
    };
    init_hide();


    // Facet Show more/less handling
    function show_more(e) {
        e.preventDefault();
        var ul = $(this).parent().parent();

        var list = ul.find('label');
        var title = ul.attr('title');

        //$(this).parent().parent().find('.read-more').text("Show Only Popular ");
        //list.parent().addClass("li-hidden");
        $(this).parent().parent().find('.read-more').addClass("hidden");
        $(this).parent().parent().find('.read-less').removeClass("hidden");

        list.parent().removeClass('li-hidden');
        list.each(function (index) {
            $(this).css("display", "block");
            //$(this).removeClass("no-bottom-border");
        });
        $('.read-less').one('click', show_less);
    };

    function show_less(e) {
        e.preventDefault();
        var ul = $(this).parent().parent();
        var list = ul.find('label');
        var title = ul.attr('title');

        //$(this).parent().parent().find('.read-more').text("Show More");
        $(this).parent().parent().find('.read-less').addClass("hidden");
        $(this).parent().parent().find('.read-more').removeClass("hidden");

        if (list.length > LIMIT) {
            list.parent().addClass("li-hidden");
        }
        list.each(function (index) {
            if (index >= LIMIT) {
                $(this).css("display", "none");
            };
            //if (index == LIMIT) {
            //    $(this).addClass("no-bottom-border");
            //}
        });
        $('.read-more').one('click', show_more);
    };

    $('.read-less').one('click', show_less);
    $('.read-more').one('click', show_more);


    //remove greek accented characters
    function remove_accented(str) {
        return str.replace('Ά', 'Α').replace('Έ', 'Ε').replace('Ή', 'Η').replace('Ί', 'Ι').replace('Ό', 'Ο').replace('Ύ', 'Υ').replace('Ώ', 'Ω');
    };

}