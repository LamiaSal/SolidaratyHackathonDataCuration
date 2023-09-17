import re
from typing import Union
import folium
import pandas as pd
from folium import plugins
import streamlit as st

EPICENTER_LOCATION = [31.12210171476489, -8.42945837915193]
BORDER_COLOR = "black"
DOUARS_URL = "../../data/regions.json"


# @st.cache_resource
def parse_gg_sheet(url):
    print("Parsing Google Sheet:", url)
    url = url.replace("edit#gid=", "export?format=csv&gid=")
    df = pd.read_csv(url, on_bad_lines="warn")
    return df


def parse_json_file(url):
    df = pd.read_json(url)
    df = pd.json_normalize(df.douars)
    return df


douar_df = parse_json_file(DOUARS_URL)


def is_request_in_list(request, selection_list, options):
    if isinstance(request, float):  # Check if the input is a float (like NaN)
        return False

    if "," in request:
        all_requests = [r.strip() for r in request.split(",")]
    else:
        all_requests = [request]

    # If at least one of the requests is not in the options or in the selection list, return True
    for r in all_requests:
        if r not in options:
            return True
        if r in selection_list:
            return True
    return False


def marker_request(request):
    # in case of multiple requests we use the first one for the marker's icon
    # requests are already sorted by priority from the form
    try:
        displayed_request = request.split(",")[0]
    except:
        displayed_request = request
    return displayed_request


def add_latlng_col(df, process_column: Union[str, int]):
    """Add a latlng column to the dataframe"""
    if isinstance(process_column, str):
        df["latlng"] = df[process_column].apply(parse_latlng)
    elif isinstance(process_column, int):
        df["latlng"] = df.iloc[:, process_column].apply(parse_latlng)
    else:
        raise ValueError(
            f"process_column should be a string or an integer, got {type(process_column)}"
        )
    return df


# parse latlng (column 4) to [lat, lng]
def parse_latlng(latlng):
    if pd.isna(latlng):
        return None
        # lat, lng = latlng.split(",")
        # return [float(lat), float(lng)]

    try:
        # check if it matches (30.9529832, -7.1010705) or (30.9529832,-7.1010705)
        if re.match(r"\(\d+\.\d+,\s?-\d+\.\d+\)", latlng):
            lat, lng = latlng[1:-1].split(",")
            return [float(lat), float(lng)]
        # check of it matches 30.9529832, -7.1010705 or 30.9529832,-7.1010705 or 30.9529832 ,-7.10107050
        elif re.match(r"\d+\.\d+\s?,\s?-\d+\.\d+", latlng):
            lat, lng = latlng.split(",")
            return [float(lat), float(lng)]
        # check if it matches 30,9529832, -7,1010705 or 30,9529832,-7,1010705, match1=30,9529832 and match2=-7,1010705
        elif re.match(r"\d+,\d+,\s?-\d+,\d+", latlng):
            d1, d2, d3, d4 = latlng.split(",")
            return [float(".".join([d1, d2])), float(".".join([d3, d4]))]
    except Exception as e:
        print(f"Error parsing latlng: {latlng}  Reason: {e}")
        return None
    print(f"Error parsing latlng: {latlng}")
    return None


def add_epicentre_to_map(fg):
    # Removed the spinner to not confuse the users as the map is already loaded
    icon_epicentre = folium.plugins.BeautifyIcon(
        icon="star",
        border_color="#b3334f",
        background_color="#b3334f",
        text_color="white",
    )

    fg.add_child(
        folium.Marker(
            location=EPICENTER_LOCATION,
            #   popup="Epicenter مركز الزلزال",
            tooltip="Epicenter مركز الزلزال",
            icon=icon_epicentre,
        )
    )


def add_danger_distances_to_map(map_obj):
    Danger_Distances_group = folium.FeatureGroup(
        name="Danger distances - earthquake magnitude 7 | مسافات الخطر - قوة الزلازل 7"
    ).add_to(map_obj)

    zones = [
        {
            "radius": 100000,
            "fill_opacity": 0.1,
            "weight": 1,
            "fill_color": "yellow",
            "tooltip": "50 to 100 km - Moderate risk area | منطقة خطر معتدلة",
        },
        {
            "radius": 50000,
            "fill_opacity": 0.1,
            "weight": 1,
            "fill_color": "orange",
            "tooltip": "30 to 50 km - High risk zone | منطقة عالية المخاطر",
        },
        {
            "radius": 30000,
            "fill_opacity": 0.2,
            "weight": 1,
            "fill_color": "#FF0000",
            "tooltip": "10 to 30 km - Very high risk zone | منطقة شديدة الخطورة",
        },
        {
            "radius": 10000,
            "fill_opacity": 0.2,
            "weight": 0.2,
            "fill_color": "#8B0000",
            "tooltip": "0 to 10km - direct impact zone | منطقة التأثير المباشر",
        },
    ]

    for zone in zones:
        folium.Circle(
            location=EPICENTER_LOCATION,
            radius=zone["radius"],
            color=BORDER_COLOR,
            weight=zone["weight"],
            fill_opacity=zone["fill_opacity"],
            opacity=zone[
                "fill_opacity"
            ],  # Assuming border opacity should match fill_opacity
            fill_color=zone["fill_color"],
            # tooltip=zone["tooltip"],
        ).add_to(Danger_Distances_group)


def add_village_names(douar_df, map_obj):
    village_fgroup = folium.FeatureGroup(
        name="🔵 All the Villages / Tous les villages / جميع القرى", show=False
    ).add_to(map_obj)

    for _, row in douar_df.iterrows():
        lat = row["lat"]
        lng = row["lng"]
        lat_lng = (lat, lng)
        dour_name = row["name"].capitalize()
        maps_url = f"https://maps.google.com/?q={lat_lng}"
        display_text = f'<br><b>⛰️ Douar:</b> {dour_name}<br><a href="{maps_url}" target="_blank" rel="noopener noreferrer"><b>🧭 Google Maps</b></a>'

        folium.CircleMarker(
            location=[lat, lng],
            radius=0.1,
            tooltip=dour_name,  # we might remove the tooltip to avoid crowding the map
            popup=folium.Popup(display_text, max_width=200),
            color="#0046C8",
            opacity=0.7,
        ).add_to(village_fgroup)


def init_map():
    m = folium.Map(
        location=[31.228674, -7.992047],
        zoom_start=8.5,
        min_zoom=8.5,
        max_lat=35.628674,
        min_lat=29.628674,
        max_lon=-4.992047,
        min_lon=-10.992047,
        max_bounds=True,
    )
    # Add a search bar to the map
    geocoder = plugins.Geocoder(
        collapsed=False,
        position="topright",
        placeholder="Search | البحث",
    )
    m.add_child(geocoder)

    # Add Fullscreen button to the map
    fullscreen = plugins.Fullscreen(
        position="topright",
        title="Expand me | تكبير الخريطة",
        title_cancel="Exit me | تصغير الخريطة",
        force_separate_button=True,
    )
    m.add_child(fullscreen)

    # Satellite View from Mapbox
    tileurl = "https://marocmap.ikiker.com/maroc/{z}/{x}/{y}.png"
    folium.TileLayer(
        tiles=tileurl,
        attr="Maroc Map",
        name="Maroc Map",
        overlay=False,
        control=False,
    ).add_to(m)

    # Add danger zones
    add_epicentre_to_map(m)
    add_danger_distances_to_map(m)
    add_village_names(douar_df, m)

    # Add a LayerControl to the map to toggle between layers (Satellite View and Default One)
    folium.LayerControl().add_to(m)

    # Add detect location button
    plugins.LocateControl(
        position="topleft",
        drawCircle=False,
        flyTo=True,
        strings={"title": "My location | موقعي", "popup": "My location | موقعي"},
    ).add_to(m)

    return m
