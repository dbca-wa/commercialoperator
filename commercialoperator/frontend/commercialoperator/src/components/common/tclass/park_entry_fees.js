const EXEMPT_PARK_NAME = /^(yanchep|nambung)\b/i;

export function isSeparateParkEntryFee(parkName) {
    return EXEMPT_PARK_NAME.test(String(parkName || '').trim());
}

function visitorCount(value) {
    const count = Number.parseInt(value, 10);
    return Number.isFinite(count) ? Math.max(count, 0) : 0;
}

function getPreviousVisitorsByDate(options) {
    const visitorsByDate = new Map();

    for (const option of options) {
        if (isSeparateParkEntryFee(option.label)) {
            continue;
        }

        for (const [arrival, visitors] of Object.entries(
            option.max_group_arrival_by_date || {}
        )) {
            const previous = visitorsByDate.get(arrival) || [0, 0, 0];
            visitorsByDate.set(arrival, [
                Math.max(previous[0], visitorCount(visitors.total_adults)),
                Math.max(previous[1], visitorCount(visitors.total_children)),
                Math.max(
                    previous[2],
                    visitorCount(visitors.total_free_of_charge)
                ),
            ]);
        }
    }

    return visitorsByDate;
}

export function calculateParkEntryFees(rows, options) {
    const optionsById = new Map(
        options.map((option) => [String(option.value), option])
    );
    const previousVisitorsByDate = getPreviousVisitorsByDate(options);
    const visitorsByDate = new Map();

    return rows.map((row) => {
        const calculatedRow = [...row];
        const park = optionsById.get(String(row[0]));
        const arrival = row[1];

        if (!park || !arrival) {
            calculatedRow[6] = '';
            calculatedRow[7] = '';
            calculatedRow[8] = '';
            calculatedRow[9] = '';
            return calculatedRow;
        }

        const separateFee = isSeparateParkEntryFee(park.label);
        const sameTourGroup = row[2] === true;
        const applySameTourGroup = sameTourGroup && !separateFee;
        const selectedVisitors = [
            visitorCount(row[3]),
            visitorCount(row[4]),
            visitorCount(row[5]),
        ];
        const previousVisitors =
            visitorsByDate.get(arrival) ||
            previousVisitorsByDate.get(arrival) ||
            [0, 0, 0];
        const billableVisitors = applySameTourGroup
            ? selectedVisitors.map((count, index) =>
                  Math.max(count - previousVisitors[index], 0)
              )
            : selectedVisitors;

        const adultPrice = Number(park.prices?.adult) || 0;
        const childPrice = Number(park.prices?.child) || 0;
        calculatedRow[6] = (
            billableVisitors[0] * adultPrice +
            billableVisitors[1] * childPrice
        ).toFixed(2);
        calculatedRow[7] = applySameTourGroup
            ? String(billableVisitors[0])
            : '';
        calculatedRow[8] = applySameTourGroup
            ? String(billableVisitors[1])
            : '';
        calculatedRow[9] = applySameTourGroup
            ? String(billableVisitors[2])
            : '';

        if (!separateFee) {
            visitorsByDate.set(arrival, [
                Math.max(previousVisitors[0], selectedVisitors[0]),
                Math.max(previousVisitors[1], selectedVisitors[1]),
                Math.max(previousVisitors[2], selectedVisitors[2]),
            ]);
        }

        return calculatedRow;
    });
}
