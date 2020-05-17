$(function () {
    // Top of page carousel
    $(".carousel:not(.edit)").slick({
        autoplay: true,
        arrows: false,
        fade: true,
        speed: 2000,
        autoplaySpeed: 5000,
        infinite: true,
    });

    var slick_started = false;

    $(window).on("popstate", function (e) {
        if (!slick_started) {
            return;
        }

        // Deconstruct slick
        $(".stop-slideshow").hide();
        $(".big-photos").slick("unslick");
        $(".photos").slick("unslick");
        slick_started = false;
    });

    $(".show-photos .stop-slideshow").on("click", function (e) {
        e.preventDefault();
        window.history.back();
    });

    function startSlideshow(id) {
        if (slick_started) return;

        slick_started = true;

        $(".stop-slideshow").show();

        $(".big-photos").slick({
            slidesToShow: 1,
            slidesToScroll: 1,
            arrows: true,
            fade: true,
            asNavFor: ".photos",
            lazyLoad: "ondemand",
            infinite: false,
        });

        $(".photos")
            .slick({
                variableWidth: true,
                centerMode: true,
                swipeToSlide: true,
                infinite: false,
                asNavFor: ".big-photos",
                focusOnSelect: true,
            })
            .slick("slickGoTo", id, true)
            .on("beforeChange", function (e, slick, currentSlide, nextSlide) {
                window.history.replaceState({}, "", "#" + nextSlide);
            });
    }

    // When clicking on a photo, show the slideshow
    $(".show-photos .photo").on("click", function () {
        if (!slick_started) {
            var id = $(this).data("id");
            startSlideshow(id);
            window.history.pushState({}, "", "#" + id);
        }
    });

    // Check if we should load a photo from the start
    if (window.location.hash) {
        var id = window.location.hash.substring(1);
        startSlideshow(id);
    }

    // Inschrijfformulier
    $("input[name=geslacht]").on("change", function () {
        var pronoun = "haar";
        if ($(this).filter(":checked").val() === "M") {
            pronoun = "zijn";
        }
        $("label[for=id_voornaam]").text("Wat is " + pronoun + " voornaam?");
        $("label[for=id_achternaam]").text("Wat is " + pronoun + " achternaam?");
        $("label[for=id_adres]").text("Wat is " + pronoun + " adres?");
        $("label[for=id_postcode]").text("Wat is " + pronoun + " postcode?");
        $("label[for=id_woonplaats]").text("Wat is " + pronoun + " woonplaats?");
    });

    for (let i = 1; i <= 5; i++) {
        $(`#row_id_kind${i}_naam`).hide();
        $(`#row_id_kind${i}_leeftijd`).hide();
    }
    
    $('#id_kinderen').on('change', (e) => {
        let kids = Number.parseInt(e.target.value);

        for (let i = 1; i <= 5; i++) {
            if (i <= kids) {
                $(`#row_id_kind${i}_naam`).slideDown();
                $(`#row_id_kind${i}_leeftijd`).slideDown();
            } else {
                $(`#row_id_kind${i}_naam`).slideUp();
                $(`#row_id_kind${i}_leeftijd`).slideUp();
            }
        }


    })
});
