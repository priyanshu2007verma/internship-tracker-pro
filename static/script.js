const canvas = document.getElementById("statusChart");

if (canvas) {

    const applied = parseInt(canvas.dataset.applied) || 0;
    const interviews = parseInt(canvas.dataset.interviews) || 0;
    const offers = parseInt(canvas.dataset.offers) || 0;
    const rejected = parseInt(canvas.dataset.rejected) || 0;

    console.log(
        applied,
        interviews,
        offers,
        rejected
    );

    new Chart(canvas, {

        type: "bar",

        data: {

            labels: [
                "Applied",
                "Interview",
                "Offer",
                "Rejected"
            ],

            datasets: [{

                label: "Applications",

                data: [
                    applied,
                    interviews,
                    offers,
                    rejected
                ]

            }]
        }
    });

}