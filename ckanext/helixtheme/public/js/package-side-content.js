jQuery(document).ready(function ($, _) {

    var console = window.console
    var debug = $.proxy(console, 'debug')

    handleSideContent();
});



function handleSideContent() {

    function init() {
        // turn to uppercase and remove greek accent 
        var sections = $('.results-main-sidebar .side-content');
        var list = sections.find('a');
        list.each(function (index) {$(this).text($(this).text().toUpperCase().replace(/Ά/g, 'Α').replace(/Έ/g, 'Ε').replace(/Ή/g, 'Η').replace(/Ί/g, 'Ι').replace( /Ό/g, 'Ο').replace(/Ύ/g, 'Υ').replace(/Ώ/g, 'Ω'));
        });
    };
    init();


}
