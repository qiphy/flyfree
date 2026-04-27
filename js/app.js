// FlyFree Frontend — reads directly from Supabase

let supabaseClient = null;
let allFlights = [];
let airports = {};

function initSupabase() {
    const url = FLYFREE_CONFIG.SUPABASE_URL;
    const key = FLYFREE_CONFIG.SUPABASE_ANON_KEY;

    if (!url || !key) {
        document.getElementById('flights-grid').innerHTML =
            '<div class="empty-state"><p>Configure Supabase credentials in js/config.js</p></div>';
        return false;
    }
    supabaseClient = window.supabase.createClient(url, key);
    return true;
}

async function loadAirports() {
    if (!supabaseClient) return;
    const { data, error } = await supabaseClient.from('airports').select('*');
    if (error) {
        console.error('Failed to load airports:', error);
        return;
    }
    data.forEach(a => {
        airports[a.iata_code] = a;
    });

    const originSelect = document.getElementById('origin');
    const destSelect = document.getElementById('destination');

    const sorted = Object.entries(airports).sort((a, b) => a[1].city.localeCompare(b[1].city));
    sorted.forEach(([code, info]) => {
        const label = `${code} — ${info.city}`;
        originSelect.add(new Option(label, code));
        destSelect.add(new Option(label, code));
    });
}

async function fetchFlights() {
    if (!supabaseClient) return;

    const grid = document.getElementById('flights-grid');
    grid.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

    let query = supabaseClient
        .from('cheapest_flights')
        .select('*');

    const origin = document.getElementById('origin').value;
    const destination = document.getElementById('destination').value;
    const flightDate = document.getElementById('date').value;

    if (origin) query = query.eq('origin', origin);
    if (destination) query = query.eq('destination', destination);
    if (flightDate) query = query.eq('flight_date', flightDate);

    const { data, error } = await query;

    if (error) {
        console.error('Failed to fetch flights:', error);
        grid.innerHTML = '<div class="empty-state"><p>Failed to load flights</p><p class="hint">Check your Supabase configuration</p></div>';
        return;
    }

    allFlights = data || [];
    sortAndRender();
}

function sortAndRender() {
    const sortValue = document.getElementById('sort').value;
    let sorted = [...allFlights];

    switch (sortValue) {
        case 'price_asc':
            sorted.sort((a, b) => a.price_myr - b.price_myr);
            break;
        case 'price_desc':
            sorted.sort((a, b) => b.price_myr - a.price_myr);
            break;
        case 'date_asc':
            sorted.sort((a, b) => a.flight_date.localeCompare(b.flight_date));
            break;
        case 'date_desc':
            sorted.sort((a, b) => b.flight_date.localeCompare(a.flight_date));
            break;
    }

    renderFlights(sorted);
}

function renderFlights(flights) {
    const grid = document.getElementById('flights-grid');
    const countEl = document.getElementById('result-count');

    if (flights.length === 0) {
        grid.innerHTML = '<div class="empty-state"><p>No flights under RM50 found</p><p class="hint">Try adjusting your filters or check back later</p></div>';
        countEl.textContent = '0 flights found';
        return;
    }

    countEl.textContent = `${flights.length} flight${flights.length !== 1 ? 's' : ''} found`;

    grid.innerHTML = flights.map(f => {
        const originCity = airports[f.origin]?.city || f.origin;
        const destCity = airports[f.destination]?.city || f.destination;
        const depTime = f.departure_time ? new Date(f.departure_time).toLocaleTimeString('en-MY', { hour: '2-digit', minute: '2-digit' }) : '—';
        const arrTime = f.arrival_time ? new Date(f.arrival_time).toLocaleTimeString('en-MY', { hour: '2-digit', minute: '2-digit' }) : '—';
        const dateStr = f.flight_date ? new Date(f.flight_date + 'T00:00:00').toLocaleDateString('en-MY', { day: 'numeric', month: 'short', year: 'numeric' }) : '—';

        return `
        <div class="flight-card">
            <div class="flight-card-header">
                <div class="flight-route">${f.origin} <span>→</span> ${f.destination}</div>
                <div class="flight-price">RM${Math.round(f.price_myr)}</div>
            </div>
            <div class="flight-details">
                <div class="flight-detail-row">
                    <span>Route</span>
                    <span class="value">${originCity} → ${destCity}</span>
                </div>
                <div class="flight-detail-row">
                    <span>Date</span>
                    <span class="value">${dateStr}</span>
                </div>
                <div class="flight-detail-row">
                    <span>Time</span>
                    <span class="value">${depTime} — ${arrTime}</span>
                </div>
                <div class="flight-detail-row">
                    <span>Airline</span>
                    <span class="value">${f.airline_name ? `<span class="flight-airline">${f.airline_name}</span>` : f.airline_code || '—'}</span>
                </div>
            </div>
        </div>`;
    }).join('');
}

function applyFilters() {
    fetchFlights();
}

// Event listeners
document.getElementById('origin').addEventListener('change', applyFilters);
document.getElementById('destination').addEventListener('change', applyFilters);
document.getElementById('date').addEventListener('change', applyFilters);
document.getElementById('sort').addEventListener('change', () => sortAndRender());

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    if (initSupabase()) {
        await loadAirports();
        await fetchFlights();
    }
});
