
    (function () {
        function cleanEmptyParameters() {
            document.querySelectorAll(
                '.swagger-ui .opblock-section'
            ).forEach(section => {
                const header = section.querySelector(
                    '.opblock-section-header'
                );

                if (!header) {
                    return;
                }

                const heading = header.querySelector('h4');

                if (
                    !heading ||
                    heading.textContent.trim() !== 'Parameters'
                ) {
                    return;
                }

                const container = section.querySelector(
                    '.parameters-container'
                );

                if (!container) {
                    return;
                }

                const hasRealParameters = Boolean(
                    container.querySelector(
                        'table, input, select, textarea'
                    )
                );

                const isEmpty = !hasRealParameters;

                if (isEmpty) {
                    heading.style.display = 'none';
                    container.style.display = 'none';
                } else {
                    heading.style.display = '';
                    container.style.display = '';
                }
            });
        }

        let updateScheduled = false;

        const observer = new MutationObserver(function () {
            if (updateScheduled) {
                return;
            }

            updateScheduled = true;

            requestAnimationFrame(function () {
                updateScheduled = false;
                cleanEmptyParameters();
            });
        });

        observer.observe(document.documentElement, {
            childList: true,
            subtree: true,
        });

        cleanEmptyParameters();
    })();
