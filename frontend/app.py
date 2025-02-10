import streamlit as st
import requests
from datetime import date, datetime, timedelta

API_BASE = "http://backend:8000"

def page_calculator():
    """
    Página que contiene la lógica de cálculo de amarres
    y comparación de puertos.
    """
    st.title("Marina Mooring Price Calculator")

    st.markdown("""
    This interface helps you:
    1. Calculate mooring rates for your boat
    2. Compare different ports
    3. (Mock) Check occupancy & reserve
    """, help="Use the sidebar to navigate other sections")

    # ----------- Price Section -----------
    st.header("Calculate Mooring Price")

    port_name = st.selectbox("Select port:", ["Puerto Benalmadena", "Puerto Marbella"])
    boat_length = st.number_input("Boat length (meters):", min_value=5.0, max_value=30.0, value=8.0)
    arrival = st.date_input("Arrival date:", value=date.today())
    departure = st.date_input("Departure date:", value=date.today())
    want_elec = st.checkbox("Do you want Electricity?", value=False)
    want_water = st.checkbox("Do you want Water?", value=False)

    if st.button("Calculate"):
        payload = {
            "port_name": port_name,
            "boat_length": boat_length,
            "arrival_date": str(arrival),
            "departure_date": str(departure),
            "want_electricity": want_elec,
            "want_water": want_water
        }
        try:
            resp = requests.post(f"{API_BASE}/calculate_price", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                st.success(f"**Total Price**: €{data['total_price']}\n\nDetails: {data['detail']}")
            else:
                st.error(resp.text)
        except Exception as ex:
            st.error(str(ex))

    # ----------- Compare Ports -----------
    st.header("Compare with Another Port")
    st.write("We'll do the same payload but for the other port to see approximate cost.")
    if st.button("Compare Ports"):
        other_port = "Puerto Marbella" if port_name == "Puerto Benalmadena" else "Puerto Benalmadena"
        payload = {
            "port_name": other_port,
            "boat_length": boat_length,
            "arrival_date": str(arrival),
            "departure_date": str(departure),
            "want_electricity": want_elec,
            "want_water": want_water
        }
        try:
            resp = requests.post(f"{API_BASE}/calculate_price", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                st.info(f"**{other_port}** => €{data['total_price']} ( {data['detail']} )")
            else:
                st.error(resp.text)
        except Exception as ex:
            st.error(str(ex))

    # ----------- Mock Occupancy -----------
    st.header("Check Occupancy (Mock)")
    st.write("We do not have real occupancy data yet, but here's a random mock.")
    if st.button("Check Occupancy"):
        occ_payload = {
            "port_name": port_name,
            "boat_length": boat_length
        }
        try:
            resp = requests.post(f"{API_BASE}/check_occupancy", json=occ_payload)
            if resp.status_code == 200:
                data = resp.json()
                st.write("**Availability for next ~30 days** (random data):")
                st.table(data)
            else:
                st.error(resp.text)
        except Exception as ex:
            st.error(str(ex))

def page_cargo_ports():
    """
    Página que muestra información sobre puertos de mercancía.
    (ejemplo de sección adicional en la interfaz)
    """
    st.title("Cargo Ports Information")
    st.markdown("""
    In this section, we might display details about cargo ports,
    big ships, arrival & departure schedules, or handle industrial freight queries.

    *This is just a placeholder to illustrate a separate page in the sidebar.*
    """, help="Expand this with real data if needed.")

def page_reservations():
    """
    Página de reserva con un pequeño calendario y un formulario,
    y una imagen de la marina al final.
    """
    st.title("Reservation")
    st.markdown("Pick your **reservation date range**:")

    default_start = date.today()
    default_end = date.today() + timedelta(days=3)
    date_range = st.date_input(
        "Reservation Date Range",
        value=(default_start, default_end)
    )
    if isinstance(date_range, tuple):
        arr, dep = date_range
        st.write(f"Selected arrival: **{arr}**, departure: **{dep}**.")
    else:
        st.write(f"Selected day: {date_range}")

    st.markdown("Fill in your boat details to confirm reservation:")
    with st.form("reservation_form"):
        boat_name = st.text_input("Boat Name:")
        boat_length = st.number_input("Boat length (m):", 5.0, 50.0, 10.0)
        contact_email = st.text_input("Contact email:")
        submitted = st.form_submit_button("Reserve Now")

        if submitted:
            st.success(
                f"Reservation requested for boat **{boat_name}**, length={boat_length}m. "
                f"We'll contact you to the email {contact_email} soon."
            )
            # Podrías hacer un requests.post al backend para guardar la reserva.

    # Mostrar una imagen de la marina
    st.markdown("---")  # separador
    st.markdown("**Check out our Marina:**")
    # Ajusta la ruta de tu imagen aquí:
    st.image("images/marina_view.png", caption="Beautiful Marina View", width=1200)
    # use_container_width=True)

def main():
    st.set_page_config(
        page_title="Marine MVP",
        page_icon="⚓",
        layout="wide"
    )

    # CSS global
    st.markdown(
        """
        <style>
            /* Fondo de la app en blanco */
            body, .stApp {
                background-color: #ffffff;
            }

            /* Texto global en negro */
            .stApp, .stApp * {
                color: #646464 !important;
            }

            /* Sidebar - Texto blanco */
            [data-testid="stSidebar"] * {
                color: #ffffff !important;
            }

            /* Mensajes de alerta */
            .stAlert[data-baseweb="alert"] {
                background-color: #f7f7f7;
                border-left: 5px solid #999999;
            }
            .stAlert[data-baseweb="alert"] * {
                color: #000000 !important;
            }

            /* Selectbox - Texto seleccionado */
            div[data-baseweb="select"] > div:first-child > div[role="button"] > div > span {
                color: #ffffff !important;
                background-color: #f7f7f7 !important;
            }

            /* Dropdown - Opciones */
            div[role="listbox"] li {
                color: #ffffff !important;
                background-color: #f7f7f7 !important;
            }

            /* Campos de formulario */
            .stTextInput input,
            .stNumberInput input,
            .stDateInput input {
                color: #333333 !important;
                background-color: #f7f7f7 !important;
            }

            /* Todos los botones principales */
            .stButton > button,
            button[data-testid="baseButton-secondary"],
            div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] button {
                color: #ffffff !important;
                background-color: #f7f7f7 !important;
                border: 1px solid #ffffff !important;
            }

            /* Botón específico del formulario "Reserve Now" */
            form[data-testid="stForm"] button[type="submit"] {
                color: #ffffff !important;
                background-color: #f7f7f7 !important;
                border: 1px solid #ffffff !important;
            }

            /* Hover botones */
            .stButton > button:hover,
            button[data-testid="baseButton-secondary"]:hover,
            div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] button:hover {
                background-color: #444444 !important;
            }
            table thead tr th:nth-child(4),
            table tbody tr td:nth-child(4) {
                   text-align: center !important;
            }
            table,
            table th,
            table td {
                border-spacing: 0 !important;   /* cero espacio entre celdas */
                padding: 6px !important;        /* reduce el padding a tu gusto */
                margin: 0 auto !important;      /* centrar la tabla si lo deseas */
            }

            table {
                width: 80% !important;          /* ancho total (ajústalo a tu gusto) */
                table-layout: fixed !important; /* para forzar columnas equidistantes */
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Sidebar
    st.sidebar.title("Marine MVP")
    choice = st.sidebar.radio(
        "Select a page",
        ["Mooring Calculator", "Cargo Ports", "Reservations"]
    )

    if choice == "Mooring Calculator":
        page_calculator()
    elif choice == "Cargo Ports":
        page_cargo_ports()
    else:
        page_reservations()

if __name__ == "__main__":
    main()
