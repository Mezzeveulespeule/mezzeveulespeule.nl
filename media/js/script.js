$(function () {
    // Top of page carousel
    $('.carousel:not(.edit)').slick({
        autoplay: true,
        arrows: false,
        fade: true,
        speed: 2000,
        autoplaySpeed: 5000,
        infinite: true
    });

    var slick_started = false;

    $(window).on('popstate', function (e) {
        if (!slick_started) {
            return;
        }

        // Deconstruct slick
        $('.stop-slideshow').hide();
        $('.big-photos').slick('unslick');
        $('.photos').slick('unslick');
        slick_started = false;

    });

    $('.show-photos .stop-slideshow').on('click', function (e) {
        e.preventDefault();
        window.history.back();
    });

    function startSlideshow(id) {
        if (slick_started)
            return;

        slick_started = true;

        $('.stop-slideshow').show();

        $('.big-photos').slick({
            slidesToShow: 1,
            slidesToScroll: 1,
            arrows: true,
            fade: true,
            asNavFor: '.photos',
            lazyLoad: 'ondemand',
            infinite: false
        });


        $('.photos').slick({
            variableWidth: true,
            centerMode: true,
            swipeToSlide: true,
            infinite: false,
            asNavFor: '.big-photos',
            focusOnSelect: true
        })
            .slick('slickGoTo', id, true)
            .on('beforeChange', function (e, slick, currentSlide, nextSlide) {

                window.history.replaceState({}, '', '#' + nextSlide);
            });

    }

    // When clicking on a photo, show the slideshow
    $('.show-photos .photo').on('click', function () {
        if (!slick_started) {
            var id = $(this).data('id');
            startSlideshow(id);
            window.history.pushState({}, '', '#' + id);
        }
    });

    // Check if we should load a photo from the start
    if (window.location.hash) {
        var id = window.location.hash.substring(1);
        startSlideshow(id);
    }
});

