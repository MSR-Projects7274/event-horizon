/* Special Event Behaviour */

document.addEventListener('DOMContentLoaded', function () {

    const specialEvent = document.querySelector('.special-event');

    /*
     * Stop here if this isn't a special event.
     *
     * This means normal Event Horizon events
     * are completely unaffected.
     */
    if (!specialEvent) {
        return;
    }


    /* Special Event Image */

    const imageContainer =
        document.querySelector('.special-image-container');

    const specialImage =
        document.querySelector('.special-event-image');

    if (imageContainer && specialImage) {

        imageContainer.addEventListener('mousemove', function (event) {

            const rect =
                imageContainer.getBoundingClientRect();

            const x =
                event.clientX - rect.left;

            const y =
                event.clientY - rect.top;

            const moveX =
                (x / rect.width - 0.5) * 30;

            const moveY =
                (y / rect.height - 0.5) * 30;

            specialImage.style.transform =
                `translate(${moveX}px, ${moveY}px)`;
        });


        imageContainer.addEventListener('mouseleave', function () {

            specialImage.style.transform =
                'translate(0, 0)';
        });
    }


    /* Special Event Whisper */

    const whisper =
        document.querySelector('.special-event-whisper');

    if (whisper) {

        const whispers = [
            'Everything is exactly as it should be.',
            'You should probably keep reading.',
            'Nothing unusual has been reported.',
            'Please do not worry.',
            'You are still here.',
            'This event is perfectly safe.',
            'We recommend arriving early.',
            'They have been expecting you.',
            'There is nothing to be concerned about.',
            'You were not supposed to notice that.',
            'Please continue as normal.',
            'Everything is under control.'
        ];

        let currentMessage = '';


        /* Pick a Message */

        const getRandomMessage = function () {

            let nextMessage;

            do {
                nextMessage =
                    whispers[
                        Math.floor(
                            Math.random() * whispers.length
                        )
                    ];
            }
            while (
                nextMessage === currentMessage &&
                whispers.length > 1
            );

            currentMessage = nextMessage;

            return nextMessage;
        };


        /* Type Message */

        const typeMessage = function (message) {

            whisper.textContent = '';

            let index = 0;

            const typeNext = function () {

                if (index >= message.length) {

                    /*
                    * Message is complete.
                    * Keep it visible.
                    */
                    setTimeout(function () {

                        eraseMessage(message);

                    }, 6000);

                    return;
                }

                whisper.textContent =
                    message.substring(0, index + 1);

                index++;

                setTimeout(
                    typeNext,
                    70
                );
            };

            typeNext();
        };


        /* Erase Message */

        const eraseMessage = function (message) {

            let index = message.length;

            const eraseNext = function () {

                if (index <= 0) {

                    whisper.textContent = '';

                    /*
                    * Nothing happens here until
                    * this timer finishes.
                    */
                    setTimeout(function () {

                        startNextMessage();

                    }, 10000);

                    return;
                }

                index--;

                whisper.textContent =
                    message.substring(0, index);

                setTimeout(
                    eraseNext,
                    90
                );
            };

            eraseNext();
        };


        /* Start the next message */

        const startNextMessage = function () {

            const nextMessage =
                getRandomMessage();

            typeMessage(nextMessage);
        };


        /* First message */

        setTimeout(function () {

            startNextMessage();

        }, 3000);

    }

    /* Special Booking Button */

    const specialBookButton =
        document.querySelector('.special-book-button');

    if (specialBookButton) {

        specialBookButton.addEventListener(
            'click',
            function (event) {

                if (this.dataset.confirmed !== 'true') {

                    event.preventDefault();

                    this.textContent =
                        'Are You Sure?';

                    this.dataset.confirmed =
                        'true';
                }
            }
        );


        specialBookButton.addEventListener(
            'mouseleave',
            function () {

                this.textContent =
                    'Book Now';

                this.dataset.confirmed =
                    'false';
            }
        );
    }

});
