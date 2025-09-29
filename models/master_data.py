from odoo import _

REGIONS = [
    {
        "id": 1,
        "name": "Afghanistan",
        "code": 1,
        "iso_code_short": "AF",
        "iso_code_long": "AFG"
    },
    {
        "id": 2,
        "name": "Albania",
        "code": 2,
        "iso_code_short": "AL",
        "iso_code_long": "ALB"
    },
    {
        "id": 3,
        "name": "Algeria",
        "code": 3,
        "iso_code_short": "DZ",
        "iso_code_long": "DZA"
    },
    {
        "id": 4,
        "name": "American Samoa",
        "code": 4,
        "iso_code_short": "AS",
        "iso_code_long": "ASM"
    },
    {
        "id": 5,
        "name": "Andorra",
        "code": 5,
        "iso_code_short": "AD",
        "iso_code_long": "AND"
    },
    {
        "id": 6,
        "name": "Angola",
        "code": 6,
        "iso_code_short": "AO",
        "iso_code_long": "AGO"
    },
    {
        "id": 7,
        "name": "Anguilla",
        "code": 7,
        "iso_code_short": "AI",
        "iso_code_long": "AIA"
    },
    {
        "id": 8,
        "name": "Antarctica",
        "code": 8,
        "iso_code_short": "AQ",
        "iso_code_long": "ATA"
    },
    {
        "id": 9,
        "name": "Antigua and Barbuda",
        "code": 9,
        "iso_code_short": "AG",
        "iso_code_long": "ATG"
    },
    {
        "id": 10,
        "name": "Argentina",
        "code": 10,
        "iso_code_short": "AR",
        "iso_code_long": "ARG"
    },
    {
        "id": 11,
        "name": "Armenia",
        "code": 11,
        "iso_code_short": "AM",
        "iso_code_long": "ARM"
    },
    {
        "id": 12,
        "name": "Aruba",
        "code": 12,
        "iso_code_short": "AW",
        "iso_code_long": "ABW"
    },
    {
        "id": 13,
        "name": "Australia",
        "code": 13,
        "iso_code_short": "AU",
        "iso_code_long": "AUS"
    },
    {
        "id": 14,
        "name": "Austria",
        "code": 14,
        "iso_code_short": "AT",
        "iso_code_long": "AUT"
    },
    {
        "id": 15,
        "name": "Azerbaijan",
        "code": 15,
        "iso_code_short": "AZ",
        "iso_code_long": "AZE"
    },
    {
        "id": 16,
        "name": "Bahamas",
        "code": 16,
        "iso_code_short": "BS",
        "iso_code_long": "BHS"
    },
    {
        "id": 17,
        "name": "Bahrain",
        "code": 17,
        "iso_code_short": "BH",
        "iso_code_long": "BHR"
    },
    {
        "id": 18,
        "name": "Bangladesh",
        "code": 18,
        "iso_code_short": "BD",
        "iso_code_long": "BGD"
    },
    {
        "id": 19,
        "name": "Barbados",
        "code": 19,
        "iso_code_short": "BB",
        "iso_code_long": "BRB"
    },
    {
        "id": 20,
        "name": "Belarus",
        "code": 20,
        "iso_code_short": "BY",
        "iso_code_long": "BLR"
    },
    {
        "id": 21,
        "name": "Belgium",
        "code": 21,
        "iso_code_short": "BE",
        "iso_code_long": "BEL"
    },
    {
        "id": 22,
        "name": "Belize",
        "code": 22,
        "iso_code_short": "BZ",
        "iso_code_long": "BLZ"
    },
    {
        "id": 23,
        "name": "Benin",
        "code": 23,
        "iso_code_short": "BJ",
        "iso_code_long": "BEN"
    },
    {
        "id": 24,
        "name": "Bermuda",
        "code": 24,
        "iso_code_short": "BM",
        "iso_code_long": "BMU"
    },
    {
        "id": 25,
        "name": "Bhutan",
        "code": 25,
        "iso_code_short": "BT",
        "iso_code_long": "BTN"
    },
    {
        "id": 26,
        "name": "Bolivia",
        "code": 26,
        "iso_code_short": "BO",
        "iso_code_long": "BOL"
    },
    {
        "id": 27,
        "name": "Bosnia-Herzegovina",
        "code": 27,
        "iso_code_short": "BA",
        "iso_code_long": "BIH"
    },
    {
        "id": 28,
        "name": "Botswana",
        "code": 28,
        "iso_code_short": "BW",
        "iso_code_long": "BWA"
    },
    {
        "id": 29,
        "name": "Bouvet Island",
        "code": 29,
        "iso_code_short": "BV",
        "iso_code_long": "BVT"
    },
    {
        "id": 30,
        "name": "Brazil",
        "code": 30,
        "iso_code_short": "BR",
        "iso_code_long": "BRA"
    },
    {
        "id": 31,
        "name": "British Indian Ocean Territory",
        "code": 31,
        "iso_code_short": "IO",
        "iso_code_long": "IOT"
    },
    {
        "id": 32,
        "name": "British Virgin Islands",
        "code": 32,
        "iso_code_short": "VG",
        "iso_code_long": "VGB"
    },
    {
        "id": 33,
        "name": "Brunei Darussalam",
        "code": 33,
        "iso_code_short": "BN",
        "iso_code_long": "BRN"
    },
    {
        "id": 34,
        "name": "Bulgaria",
        "code": 34,
        "iso_code_short": "BG",
        "iso_code_long": "BGR"
    },
    {
        "id": 35,
        "name": "Burkina Faso",
        "code": 35,
        "iso_code_short": "BF",
        "iso_code_long": "BFA"
    },
    {
        "id": 36,
        "name": "Burundi",
        "code": 36,
        "iso_code_short": "BI",
        "iso_code_long": "BDI"
    },
    {
        "id": 37,
        "name": "Cambodia",
        "code": 37,
        "iso_code_short": "KH",
        "iso_code_long": "KHM"
    },
    {
        "id": 38,
        "name": "Cameroon",
        "code": 38,
        "iso_code_short": "CM",
        "iso_code_long": "CMR"
    },
    {
        "id": 39,
        "name": "Canada",
        "code": 39,
        "iso_code_short": "CA",
        "iso_code_long": "CAN"
    },
    {
        "id": 40,
        "name": "Cape Verde",
        "code": 40,
        "iso_code_short": "CV",
        "iso_code_long": "CPV"
    },
    {
        "id": 41,
        "name": "Cayman Islands",
        "code": 41,
        "iso_code_short": "KY",
        "iso_code_long": "CYM"
    },
    {
        "id": 42,
        "name": "Central African Republic",
        "code": 42,
        "iso_code_short": "CF",
        "iso_code_long": "CAF"
    },
    {
        "id": 43,
        "name": "Chad",
        "code": 43,
        "iso_code_short": "TD",
        "iso_code_long": "TCD"
    },
    {
        "id": 44,
        "name": "Chile",
        "code": 44,
        "iso_code_short": "CL",
        "iso_code_long": "CHL"
    },
    {
        "id": 45,
        "name": "China",
        "code": 45,
        "iso_code_short": "CN",
        "iso_code_long": "CHN"
    },
    {
        "id": 46,
        "name": "Christmas Island",
        "code": 46,
        "iso_code_short": "CX",
        "iso_code_long": "CXR"
    },
    {
        "id": 47,
        "name": "Cocos Islands",
        "code": 47,
        "iso_code_short": "CC",
        "iso_code_long": "CCK"
    },
    {
        "id": 48,
        "name": "Colombia",
        "code": 48,
        "iso_code_short": "CO",
        "iso_code_long": "COL"
    },
    {
        "id": 49,
        "name": "Comoros",
        "code": 49,
        "iso_code_short": "KM",
        "iso_code_long": "COM"
    },
    {
        "id": 50,
        "name": "Congo, Democratic Republic of",
        "code": 50,
        "iso_code_short": "CD",
        "iso_code_long": "COD"
    },
    {
        "id": 51,
        "name": "Congo",
        "code": 51,
        "iso_code_short": "CG",
        "iso_code_long": "COG"
    },
    {
        "id": 52,
        "name": "Cook Islands",
        "code": 52,
        "iso_code_short": "CK",
        "iso_code_long": "COK"
    },
    {
        "id": 53,
        "name": "Costa Rica",
        "code": 53,
        "iso_code_short": "CR",
        "iso_code_long": "CRI"
    },
    {
        "id": 54,
        "name": "Ivory Coast",
        "code": 54,
        "iso_code_short": "CI",
        "iso_code_long": "CIV"
    },
    {
        "id": 55,
        "name": "Cuba",
        "code": 55,
        "iso_code_short": "CU",
        "iso_code_long": "CUB"
    },
    {
        "id": 56,
        "name": "Cyprus",
        "code": 56,
        "iso_code_short": "CY",
        "iso_code_long": "CYP"
    },
    {
        "id": 57,
        "name": "Czech Republic",
        "code": 57,
        "iso_code_short": "CZ",
        "iso_code_long": "CZE"
    },
    {
        "id": 58,
        "name": "Denmark",
        "code": 58,
        "iso_code_short": "DK",
        "iso_code_long": "DNK"
    },
    {
        "id": 59,
        "name": "Djibouti",
        "code": 59,
        "iso_code_short": "DJ",
        "iso_code_long": "DJI"
    },
    {
        "id": 60,
        "name": "Dominica",
        "code": 60,
        "iso_code_short": "DM",
        "iso_code_long": "DMA"
    },
    {
        "id": 61,
        "name": "Dominican Republic",
        "code": 61,
        "iso_code_short": "DO",
        "iso_code_long": "DOM"
    },
    {
        "id": 62,
        "name": "Ecuador",
        "code": 62,
        "iso_code_short": "EC",
        "iso_code_long": "ECU"
    },
    {
        "id": 63,
        "name": "Egypt",
        "code": 63,
        "iso_code_short": "EG",
        "iso_code_long": "EGY"
    },
    {
        "id": 64,
        "name": "El Salvador",
        "code": 64,
        "iso_code_short": "SV",
        "iso_code_long": "SLV"
    },
    {
        "id": 65,
        "name": "Equatorial Guinea",
        "code": 65,
        "iso_code_short": "GQ",
        "iso_code_long": "GNQ"
    },
    {
        "id": 66,
        "name": "Eritrea",
        "code": 66,
        "iso_code_short": "ER",
        "iso_code_long": "ERI"
    },
    {
        "id": 67,
        "name": "Estonia",
        "code": 67,
        "iso_code_short": "EE",
        "iso_code_long": "EST"
    },
    {
        "id": 68,
        "name": "Ethiopia",
        "code": 68,
        "iso_code_short": "ET",
        "iso_code_long": "ETH"
    },
    {
        "id": 69,
        "name": "Faeroe Islands",
        "code": 69,
        "iso_code_short": "FO",
        "iso_code_long": "FRO"
    },
    {
        "id": 70,
        "name": "Falkland Islands",
        "code": 70,
        "iso_code_short": "FK",
        "iso_code_long": "FLK"
    },
    {
        "id": 71,
        "name": "Fiji",
        "code": 71,
        "iso_code_short": "FJ",
        "iso_code_long": "FJI"
    },
    {
        "id": 72,
        "name": "Finland",
        "code": 72,
        "iso_code_short": "FI",
        "iso_code_long": "FIN"
    },
    {
        "id": 73,
        "name": "France",
        "code": 73,
        "iso_code_short": "FR",
        "iso_code_long": "FRA"
    },
    {
        "id": 74,
        "name": "French Guiana",
        "code": 74,
        "iso_code_short": "GF",
        "iso_code_long": "GUF"
    },
    {
        "id": 75,
        "name": "French Polynesia",
        "code": 75,
        "iso_code_short": "PF",
        "iso_code_long": "PYF"
    },
    {
        "id": 76,
        "name": "French Southern Territories",
        "code": 76,
        "iso_code_short": "TF",
        "iso_code_long": "ATF"
    },
    {
        "id": 77,
        "name": "Gabon",
        "code": 77,
        "iso_code_short": "GA",
        "iso_code_long": "GAB"
    },
    {
        "id": 78,
        "name": "Gambia",
        "code": 78,
        "iso_code_short": "GM",
        "iso_code_long": "GMB"
    },
    {
        "id": 79,
        "name": "Georgia",
        "code": 79,
        "iso_code_short": "GE",
        "iso_code_long": "GEO"
    },
    {
        "id": 80,
        "name": "Germany",
        "code": 80,
        "iso_code_short": "DE",
        "iso_code_long": "DEU"
    },
    {
        "id": 81,
        "name": "Ghana",
        "code": 81,
        "iso_code_short": "GH",
        "iso_code_long": "GHA"
    },
    {
        "id": 82,
        "name": "Gibraltar",
        "code": 82,
        "iso_code_short": "GI",
        "iso_code_long": "GIB"
    },
    {
        "id": 83,
        "name": "Greece",
        "code": 83,
        "iso_code_short": "GR",
        "iso_code_long": "GRC"
    },
    {
        "id": 84,
        "name": "Greenland",
        "code": 84,
        "iso_code_short": "GL",
        "iso_code_long": "GRL"
    },
    {
        "id": 85,
        "name": "Grenada",
        "code": 85,
        "iso_code_short": "GD",
        "iso_code_long": "GRD"
    },
    {
        "id": 86,
        "name": "Guadaloupe",
        "code": 86,
        "iso_code_short": "GP",
        "iso_code_long": "GLP"
    },
    {
        "id": 87,
        "name": "Guam",
        "code": 87,
        "iso_code_short": "GU",
        "iso_code_long": "GUM"
    },
    {
        "id": 88,
        "name": "Guatemala",
        "code": 88,
        "iso_code_short": "GT",
        "iso_code_long": "GTM"
    },
    {
        "id": 89,
        "name": "Guinea",
        "code": 89,
        "iso_code_short": "GN",
        "iso_code_long": "GIN"
    },
    {
        "id": 90,
        "name": "Guinea-Bissau",
        "code": 90,
        "iso_code_short": "GW",
        "iso_code_long": "GNB"
    },
    {
        "id": 91,
        "name": "Guyana",
        "code": 91,
        "iso_code_short": "GY",
        "iso_code_long": "GUY"
    },
    {
        "id": 92,
        "name": "Haiti",
        "code": 92,
        "iso_code_short": "HT",
        "iso_code_long": "HTI"
    },
    {
        "id": 93,
        "name": "Heard and McDonald Islands",
        "code": 93,
        "iso_code_short": "HM",
        "iso_code_long": "HMD"
    },
    {
        "id": 94,
        "name": "Holy See",
        "code": 94,
        "iso_code_short": "VA",
        "iso_code_long": "VAT"
    },
    {
        "id": 95,
        "name": "Honduras",
        "code": 95,
        "iso_code_short": "HN",
        "iso_code_long": "HND"
    },
    {
        "id": 96,
        "name": "Hong Kong",
        "code": 96,
        "iso_code_short": "HK",
        "iso_code_long": "HKG"
    },
    {
        "id": 97,
        "name": "Croatia",
        "code": 97,
        "iso_code_short": "HR",
        "iso_code_long": "HRV"
    },
    {
        "id": 98,
        "name": "Hungary",
        "code": 98,
        "iso_code_short": "HU",
        "iso_code_long": "HUN"
    },
    {
        "id": 99,
        "name": "Iceland",
        "code": 99,
        "iso_code_short": "IS",
        "iso_code_long": "ISL"
    },
    {
        "id": 100,
        "name": "India",
        "code": 100,
        "iso_code_short": "IN",
        "iso_code_long": "IND"
    },
    {
        "id": 101,
        "name": "Indonesia",
        "code": 101,
        "iso_code_short": "ID",
        "iso_code_long": "IDN"
    },
    {
        "id": 102,
        "name": "Iran",
        "code": 102,
        "iso_code_short": "IR",
        "iso_code_long": "IRN"
    },
    {
        "id": 103,
        "name": "Iraq",
        "code": 103,
        "iso_code_short": "IQ",
        "iso_code_long": "IRQ"
    },
    {
        "id": 104,
        "name": "Ireland",
        "code": 104,
        "iso_code_short": "IE",
        "iso_code_long": "IRL"
    },
    {
        "id": 105,
        "name": "Israel",
        "code": 105,
        "iso_code_short": "IL",
        "iso_code_long": "ISR"
    },
    {
        "id": 106,
        "name": "Italy",
        "code": 106,
        "iso_code_short": "IT",
        "iso_code_long": "ITA"
    },
    {
        "id": 107,
        "name": "Jamaica",
        "code": 107,
        "iso_code_short": "JM",
        "iso_code_long": "JAM"
    },
    {
        "id": 108,
        "name": "Japan",
        "code": 108,
        "iso_code_short": "JP",
        "iso_code_long": "JPN"
    },
    {
        "id": 109,
        "name": "Jordan",
        "code": 109,
        "iso_code_short": "JO",
        "iso_code_long": "JOR"
    },
    {
        "id": 110,
        "name": "Kazakhstan",
        "code": 110,
        "iso_code_short": "KZ",
        "iso_code_long": "KAZ"
    },
    {
        "id": 111,
        "name": "Kenya",
        "code": 111,
        "iso_code_short": "KE",
        "iso_code_long": "KEN"
    },
    {
        "id": 112,
        "name": "Kiribati",
        "code": 112,
        "iso_code_short": "KI",
        "iso_code_long": "KIR"
    },
    {
        "id": 113,
        "name": "North Korea",
        "code": 113,
        "iso_code_short": "KP",
        "iso_code_long": "PRK"
    },
    {
        "id": 114,
        "name": "South Korea",
        "code": 114,
        "iso_code_short": "KR",
        "iso_code_long": "KOR"
    },
    {
        "id": 115,
        "name": "Kuwait",
        "code": 115,
        "iso_code_short": "KW",
        "iso_code_long": "KWT"
    },
    {
        "id": 116,
        "name": "Kyrgyzstan",
        "code": 116,
        "iso_code_short": "KG",
        "iso_code_long": "KGZ"
    },
    {
        "id": 117,
        "name": "Laos",
        "code": 117,
        "iso_code_short": "LA",
        "iso_code_long": "LAO"
    },
    {
        "id": 118,
        "name": "Latvia",
        "code": 118,
        "iso_code_short": "LV",
        "iso_code_long": "LVA"
    },
    {
        "id": 119,
        "name": "Lebanon",
        "code": 119,
        "iso_code_short": "LB",
        "iso_code_long": "LBN"
    },
    {
        "id": 120,
        "name": "Lesotho",
        "code": 120,
        "iso_code_short": "LS",
        "iso_code_long": "LSO"
    },
    {
        "id": 121,
        "name": "Liberia",
        "code": 121,
        "iso_code_short": "LR",
        "iso_code_long": "LBR"
    },
    {
        "id": 122,
        "name": "Libya",
        "code": 122,
        "iso_code_short": "LY",
        "iso_code_long": "LBY"
    },
    {
        "id": 123,
        "name": "Liechtenstein",
        "code": 123,
        "iso_code_short": "LI",
        "iso_code_long": "LIE"
    },
    {
        "id": 124,
        "name": "Lithuania",
        "code": 124,
        "iso_code_short": "LT",
        "iso_code_long": "LTU"
    },
    {
        "id": 125,
        "name": "Luxembourg",
        "code": 125,
        "iso_code_short": "LU",
        "iso_code_long": "LUX"
    },
    {
        "id": 126,
        "name": "Macao",
        "code": 126,
        "iso_code_short": "MO",
        "iso_code_long": "MAC"
    },
    {
        "id": 127,
        "name": "Macedonia",
        "code": 127,
        "iso_code_short": "MK",
        "iso_code_long": "MKD"
    },
    {
        "id": 128,
        "name": "Madagascar",
        "code": 128,
        "iso_code_short": "MG",
        "iso_code_long": "MDG"
    },
    {
        "id": 129,
        "name": "Malawi",
        "code": 129,
        "iso_code_short": "MW",
        "iso_code_long": "MWI"
    },
    {
        "id": 130,
        "name": "Malaysia",
        "code": 130,
        "iso_code_short": "MY",
        "iso_code_long": "MYS"
    },
    {
        "id": 131,
        "name": "Maldives",
        "code": 131,
        "iso_code_short": "MV",
        "iso_code_long": "MDV"
    },
    {
        "id": 132,
        "name": "Mali",
        "code": 132,
        "iso_code_short": "ML",
        "iso_code_long": "MLI"
    },
    {
        "id": 133,
        "name": "Malta",
        "code": 133,
        "iso_code_short": "MT",
        "iso_code_long": "MLT"
    },
    {
        "id": 134,
        "name": "Marshall Islands",
        "code": 134,
        "iso_code_short": "MH",
        "iso_code_long": "MHL"
    },
    {
        "id": 135,
        "name": "Martinique",
        "code": 135,
        "iso_code_short": "MQ",
        "iso_code_long": "MTQ"
    },
    {
        "id": 136,
        "name": "Mauritania",
        "code": 136,
        "iso_code_short": "MR",
        "iso_code_long": "MRT"
    },
    {
        "id": 137,
        "name": "Mauritius",
        "code": 137,
        "iso_code_short": "MU",
        "iso_code_long": "MUS"
    },
    {
        "id": 138,
        "name": "Mayotte",
        "code": 138,
        "iso_code_short": "YT",
        "iso_code_long": "MYT"
    },
    {
        "id": 139,
        "name": "Mexico",
        "code": 139,
        "iso_code_short": "MX",
        "iso_code_long": "MEX"
    },
    {
        "id": 140,
        "name": "Micronesia",
        "code": 140,
        "iso_code_short": "FM",
        "iso_code_long": "FSM"
    },
    {
        "id": 141,
        "name": "Moldova",
        "code": 141,
        "iso_code_short": "MD",
        "iso_code_long": "MDA"
    },
    {
        "id": 142,
        "name": "Monaco",
        "code": 142,
        "iso_code_short": "MC",
        "iso_code_long": "MCO"
    },
    {
        "id": 143,
        "name": "Mongolia",
        "code": 143,
        "iso_code_short": "MN",
        "iso_code_long": "MNG"
    },
    {
        "id": 144,
        "name": "Montserrat",
        "code": 144,
        "iso_code_short": "MS",
        "iso_code_long": "MSR"
    },
    {
        "id": 145,
        "name": "Morocco",
        "code": 145,
        "iso_code_short": "MA",
        "iso_code_long": "MAR"
    },
    {
        "id": 146,
        "name": "Mozambique",
        "code": 146,
        "iso_code_short": "MZ",
        "iso_code_long": "MOZ"
    },
    {
        "id": 147,
        "name": "Myanmar",
        "code": 147,
        "iso_code_short": "MM",
        "iso_code_long": "MMR"
    },
    {
        "id": 148,
        "name": "Namibia",
        "code": 148,
        "iso_code_short": "NA",
        "iso_code_long": "NAM"
    },
    {
        "id": 149,
        "name": "Nauru",
        "code": 149,
        "iso_code_short": "NR",
        "iso_code_long": "NRU"
    },
    {
        "id": 150,
        "name": "Nepal",
        "code": 150,
        "iso_code_short": "NP",
        "iso_code_long": "NPL"
    },
    {
        "id": 151,
        "name": "Netherlands Antilles",
        "code": 151,
        "iso_code_short": "AN",
        "iso_code_long": "ANT"
    },
    {
        "id": 152,
        "name": "Netherlands",
        "code": 152,
        "iso_code_short": "NL",
        "iso_code_long": "NLD"
    },
    {
        "id": 153,
        "name": "New Caledonia",
        "code": 153,
        "iso_code_short": "NC",
        "iso_code_long": "NCL"
    },
    {
        "id": 154,
        "name": "New Zealand",
        "code": 154,
        "iso_code_short": "NZ",
        "iso_code_long": "NZL"
    },
    {
        "id": 155,
        "name": "Nicaragua",
        "code": 155,
        "iso_code_short": "NI",
        "iso_code_long": "NIC"
    },
    {
        "id": 156,
        "name": "Niger",
        "code": 156,
        "iso_code_short": "NE",
        "iso_code_long": "NER"
    },
    {
        "id": 157,
        "name": "Nigeria",
        "code": 157,
        "iso_code_short": "NG",
        "iso_code_long": "NGA"
    },
    {
        "id": 158,
        "name": "Niue",
        "code": 158,
        "iso_code_short": "NU",
        "iso_code_long": "NIU"
    },
    {
        "id": 159,
        "name": "Norfolk Island",
        "code": 159,
        "iso_code_short": "NF",
        "iso_code_long": "NFK"
    },
    {
        "id": 160,
        "name": "Northern Mariana Islands",
        "code": 160,
        "iso_code_short": "MP",
        "iso_code_long": "MNP"
    },
    {
        "id": 161,
        "name": "Norway",
        "code": 161,
        "iso_code_short": "NO",
        "iso_code_long": "NOR"
    },
    {
        "id": 162,
        "name": "Oman",
        "code": 162,
        "iso_code_short": "OM",
        "iso_code_long": "OMN"
    },
    {
        "id": 163,
        "name": "Pakistan",
        "code": 163,
        "iso_code_short": "PK",
        "iso_code_long": "PAK"
    },
    {
        "id": 164,
        "name": "Palau",
        "code": 164,
        "iso_code_short": "PW",
        "iso_code_long": "PLW"
    },
    {
        "id": 165,
        "name": "Palestine",
        "code": 165,
        "iso_code_short": "PS",
        "iso_code_long": "PSE"
    },
    {
        "id": 166,
        "name": "Panama",
        "code": 166,
        "iso_code_short": "PA",
        "iso_code_long": "PAN"
    },
    {
        "id": 167,
        "name": "Papua New Guinea",
        "code": 167,
        "iso_code_short": "PG",
        "iso_code_long": "PNG"
    },
    {
        "id": 168,
        "name": "Paraguay",
        "code": 168,
        "iso_code_short": "PY",
        "iso_code_long": "PRY"
    },
    {
        "id": 169,
        "name": "Peru",
        "code": 169,
        "iso_code_short": "PE",
        "iso_code_long": "PER"
    },
    {
        "id": 170,
        "name": "Philippines",
        "code": 170,
        "iso_code_short": "PH",
        "iso_code_long": "PHL"
    },
    {
        "id": 171,
        "name": "Pitcairn Island",
        "code": 171,
        "iso_code_short": "PN",
        "iso_code_long": "PCN"
    },
    {
        "id": 172,
        "name": "Poland",
        "code": 172,
        "iso_code_short": "PL",
        "iso_code_long": "POL"
    },
    {
        "id": 173,
        "name": "Portugal",
        "code": 173,
        "iso_code_short": "PT",
        "iso_code_long": "PRT"
    },
    {
        "id": 174,
        "name": "Puerto Rico",
        "code": 174,
        "iso_code_short": "PR",
        "iso_code_long": "PRI"
    },
    {
        "id": 175,
        "name": "Qatar",
        "code": 175,
        "iso_code_short": "QA",
        "iso_code_long": "QAT"
    },
    {
        "id": 176,
        "name": "Reunion",
        "code": 176,
        "iso_code_short": "RE",
        "iso_code_long": "REU"
    },
    {
        "id": 177,
        "name": "Romania",
        "code": 177,
        "iso_code_short": "RO",
        "iso_code_long": "ROU"
    },
    {
        "id": 178,
        "name": "​",
        "code": 178,
        "iso_code_short": "RU",
        "iso_code_long": "RUS"
    },
    {
        "id": 179,
        "name": "Rwanda",
        "code": 179,
        "iso_code_short": "RW",
        "iso_code_long": "RWA"
    },
    {
        "id": 180,
        "name": "St. Helena",
        "code": 180,
        "iso_code_short": "SH",
        "iso_code_long": "SHN"
    },
    {
        "id": 181,
        "name": "St. Kitts and Nevis",
        "code": 181,
        "iso_code_short": "KN",
        "iso_code_long": "KNA"
    },
    {
        "id": 182,
        "name": "St. Lucia",
        "code": 182,
        "iso_code_short": "LC",
        "iso_code_long": "LCA"
    },
    {
        "id": 183,
        "name": "St. Pierre and Miquelon",
        "code": 183,
        "iso_code_short": "PM",
        "iso_code_long": "SPM"
    },
    {
        "id": 184,
        "name": "St. Vincent and the Grenadines",
        "code": 184,
        "iso_code_short": "VC",
        "iso_code_long": "VCT"
    },
    {
        "id": 185,
        "name": "Samoa",
        "code": 185,
        "iso_code_short": "WS",
        "iso_code_long": "WSM"
    },
    {
        "id": 186,
        "name": "San Marino",
        "code": 186,
        "iso_code_short": "SM",
        "iso_code_long": "SMR"
    },
    {
        "id": 187,
        "name": "Sao Tome and Principe",
        "code": 187,
        "iso_code_short": "ST",
        "iso_code_long": "STP"
    },
    {
        "id": 188,
        "name": "Saudi Arabia",
        "code": 188,
        "iso_code_short": "SA",
        "iso_code_long": "SAU"
    },
    {
        "id": 189,
        "name": "Senegal",
        "code": 189,
        "iso_code_short": "SN",
        "iso_code_long": "SEN"
    },
    {
        "id": 190,
        "name": "Serbia",
        "code": 190,
        "iso_code_short": "RS",
        "iso_code_long": "SRB"
    },
    {
        "id": 191,
        "name": "Seychelles",
        "code": 191,
        "iso_code_short": "SC",
        "iso_code_long": "SYC"
    },
    {
        "id": 192,
        "name": "Sierra Leone",
        "code": 192,
        "iso_code_short": "SL",
        "iso_code_long": "SLE"
    },
    {
        "id": 193,
        "name": "Singapore",
        "code": 193,
        "iso_code_short": "SG",
        "iso_code_long": "SGP"
    },
    {
        "id": 194,
        "name": "Slovakia",
        "code": 194,
        "iso_code_short": "SK",
        "iso_code_long": "SVK"
    },
    {
        "id": 195,
        "name": "Slovenia",
        "code": 195,
        "iso_code_short": "SI",
        "iso_code_long": "SVN"
    },
    {
        "id": 196,
        "name": "Solomon Islands",
        "code": 196,
        "iso_code_short": "SB",
        "iso_code_long": "SLB"
    },
    {
        "id": 197,
        "name": "Somalia",
        "code": 197,
        "iso_code_short": "SO",
        "iso_code_long": "SOM"
    },
    {
        "id": 198,
        "name": "South Africa",
        "code": 198,
        "iso_code_short": "ZA",
        "iso_code_long": "ZAF"
    },
    {
        "id": 199,
        "name": "South Georgia and the South Sandwich Islands",
        "code": 199,
        "iso_code_short": "GS",
        "iso_code_long": "SGS"
    },
    {
        "id": 200,
        "name": "Spain",
        "code": 200,
        "iso_code_short": "ES",
        "iso_code_long": "ESP"
    },
    {
        "id": 201,
        "name": "Sri Lanka",
        "code": 201,
        "iso_code_short": "LK",
        "iso_code_long": "LKA"
    },
    {
        "id": 202,
        "name": "Sudan",
        "code": 202,
        "iso_code_short": "SD",
        "iso_code_long": "SDN"
    },
    {
        "id": 203,
        "name": "Suriname",
        "code": 203,
        "iso_code_short": "SR",
        "iso_code_long": "SUR"
    },
    {
        "id": 204,
        "name": "Svalbard & Jan Mayen Islands",
        "code": 204,
        "iso_code_short": "SJ",
        "iso_code_long": "SJM"
    },
    {
        "id": 205,
        "name": "Eswatini",
        "code": 205,
        "iso_code_short": "SZ",
        "iso_code_long": "SWZ"
    },
    {
        "id": 206,
        "name": "Sweden",
        "code": 206,
        "iso_code_short": "SE",
        "iso_code_long": "SWE"
    },
    {
        "id": 207,
        "name": "Switzerland",
        "code": 207,
        "iso_code_short": "CH",
        "iso_code_long": "CHE"
    },
    {
        "id": 208,
        "name": "Syria",
        "code": 208,
        "iso_code_short": "SY",
        "iso_code_long": "SYR"
    },
    {
        "id": 209,
        "name": "Chinese Taipei",
        "code": 209,
        "iso_code_short": "TW",
        "iso_code_long": "TWN"
    },
    {
        "id": 210,
        "name": "Tajikistan",
        "code": 210,
        "iso_code_short": "TJ",
        "iso_code_long": "TJK"
    },
    {
        "id": 211,
        "name": "Tanzania",
        "code": 211,
        "iso_code_short": "TZ",
        "iso_code_long": "TZA"
    },
    {
        "id": 212,
        "name": "Thailand",
        "code": 212,
        "iso_code_short": "TH",
        "iso_code_long": "THA"
    },
    {
        "id": 213,
        "name": "Timor-Leste",
        "code": 213,
        "iso_code_short": "TL",
        "iso_code_long": "TLS"
    },
    {
        "id": 214,
        "name": "Togo",
        "code": 214,
        "iso_code_short": "TG",
        "iso_code_long": "TGO"
    },
    {
        "id": 215,
        "name": "Tokelau",
        "code": 215,
        "iso_code_short": "TK",
        "iso_code_long": "TKL"
    },
    {
        "id": 216,
        "name": "Tonga",
        "code": 216,
        "iso_code_short": "TO",
        "iso_code_long": "TON"
    },
    {
        "id": 217,
        "name": "Trinidad and Tobago",
        "code": 217,
        "iso_code_short": "TT",
        "iso_code_long": "TTO"
    },
    {
        "id": 218,
        "name": "Tunisia",
        "code": 218,
        "iso_code_short": "TN",
        "iso_code_long": "TUN"
    },
    {
        "id": 219,
        "name": "Turkey",
        "code": 219,
        "iso_code_short": "TR",
        "iso_code_long": "TUR"
    },
    {
        "id": 220,
        "name": "Turkmenistan",
        "code": 220,
        "iso_code_short": "TM",
        "iso_code_long": "TKM"
    },
    {
        "id": 221,
        "name": "Turks and Caicos Islands",
        "code": 221,
        "iso_code_short": "TC",
        "iso_code_long": "TCA"
    },
    {
        "id": 222,
        "name": "Tuvalu",
        "code": 222,
        "iso_code_short": "TV",
        "iso_code_long": "TUV"
    },
    {
        "id": 223,
        "name": "US Virgin Islands",
        "code": 223,
        "iso_code_short": "VI",
        "iso_code_long": "VIR"
    },
    {
        "id": 224,
        "name": "Uganda",
        "code": 224,
        "iso_code_short": "UG",
        "iso_code_long": "UGA"
    },
    {
        "id": 225,
        "name": "Ukraine",
        "code": 225,
        "iso_code_short": "UA",
        "iso_code_long": "UKR"
    },
    {
        "id": 226,
        "name": "United Arab Emirates",
        "code": 226,
        "iso_code_short": "AE",
        "iso_code_long": "ARE"
    },
    {
        "id": 227,
        "name": "United Kingdom",
        "code": 227,
        "iso_code_short": "GB",
        "iso_code_long": "GBR"
    },
    {
        "id": 228,
        "name": "United States Minor Outlying Islands",
        "code": 228,
        "iso_code_short": "UM",
        "iso_code_long": "UMI"
    },
    {
        "id": 229,
        "name": "USA",
        "code": 229,
        "iso_code_short": "US",
        "iso_code_long": "USA"
    },
    {
        "id": 230,
        "name": "Uruguay",
        "code": 230,
        "iso_code_short": "UY",
        "iso_code_long": "URY"
    },
    {
        "id": 231,
        "name": "Uzbekistan",
        "code": 231,
        "iso_code_short": "UZ",
        "iso_code_long": "UZB"
    },
    {
        "id": 232,
        "name": "Vanuatu",
        "code": 232,
        "iso_code_short": "VU",
        "iso_code_long": "VUT"
    },
    {
        "id": 233,
        "name": "Venezuela",
        "code": 233,
        "iso_code_short": "VE",
        "iso_code_long": "VEN"
    },
    {
        "id": 234,
        "name": "Vietnam",
        "code": 234,
        "iso_code_short": "VN",
        "iso_code_long": "VNM"
    },
    {
        "id": 235,
        "name": "Wallis and Futuna Islands",
        "code": 235,
        "iso_code_short": "WF",
        "iso_code_long": "WLF"
    },
    {
        "id": 236,
        "name": "Western Sahara",
        "code": 236,
        "iso_code_short": "EH",
        "iso_code_long": "ESH"
    },
    {
        "id": 237,
        "name": "Yemen",
        "code": 237,
        "iso_code_short": "YE",
        "iso_code_long": "YEM"
    },
    {
        "id": 238,
        "name": "Zambia",
        "code": 238,
        "iso_code_short": "ZM",
        "iso_code_long": "ZMB"
    },
    {
        "id": 239,
        "name": "Zimbabwe",
        "code": 239,
        "iso_code_short": "ZW",
        "iso_code_long": "ZWE"
    },
    {
        "id": 240,
        "name": "Montenegro",
        "code": 240,
        "iso_code_short": "ME",
        "iso_code_long": "MNE"
    },
    {
        "id": 241,
        "name": "England",
        "code": 241,
        "iso_code_short": "EN",
        "iso_code_long": "ENG"
    },
    {
        "id": 242,
        "name": "Northern Ireland",
        "code": 242,
        "iso_code_short": "NN",
        "iso_code_long": "NIR"
    },
    {
        "id": 243,
        "name": "Scotland",
        "code": 243,
        "iso_code_short": "S1",
        "iso_code_long": "SCO"
    },
    {
        "id": 244,
        "name": "Wales",
        "code": 244,
        "iso_code_short": "WA",
        "iso_code_long": "WAL"
    },
    {
        "id": 267,
        "name": "Aland Islands",
        "code": 267,
        "iso_code_short": "AX",
        "iso_code_long": "ALA"
    },
    {
        "id": 269,
        "name": "Saint Barthelemy",
        "code": 269,
        "iso_code_short": "BL",
        "iso_code_long": "BLM"
    },
    {
        "id": 271,
        "name": "Guernsey",
        "code": 271,
        "iso_code_short": "GG",
        "iso_code_long": "GGY"
    },
    {
        "id": 273,
        "name": "Isle of Man",
        "code": 273,
        "iso_code_short": "IM",
        "iso_code_long": "IMN"
    },
    {
        "id": 275,
        "name": "Jersey",
        "code": 275,
        "iso_code_short": "JE",
        "iso_code_long": "JEY"
    },
    {
        "id": 277,
        "name": "Saint Martin",
        "code": 277,
        "iso_code_short": "MF",
        "iso_code_long": "MAF"
    },
    {
        "id": 279,
        "name": "Bonaire, Saint Eustatius and Saba",
        "code": 279,
        "iso_code_short": "BQ",
        "iso_code_long": "BES"
    },
    {
        "id": 281,
        "name": "Curacao",
        "code": 281,
        "iso_code_short": "CW",
        "iso_code_long": "CUW"
    },
    {
        "id": 283,
        "name": "Sint Maarten",
        "code": 283,
        "iso_code_short": "SX",
        "iso_code_long": "SXM"
    },
    {
        "id": 285,
        "name": "South Sudan",
        "code": 285,
        "iso_code_short": "SS",
        "iso_code_long": "SSD"
    },
    {
        "id": 286,
        "name": "Kosovo",
        "code": 286,
        "iso_code_short": "XK",
        "iso_code_long": "RKS"
    }
]

MAPPING_SELECTIONS_DATA = {
    "element_stats" : [
        ('minutes', _('Minutes played')),
        ('goals_scored', _('Goals scored')),
        ('assists', _('Assists')),
        ('clean_sheets', _('Clean sheets')),
        ('goals_conceded', _('Goals conceded')),
        ('own_goals', _('Own goals')),
        ('penalties_saved', _('Penalties saved')),
        ('penalties_missed', _('Penalties missed')),
        ('yellow_cards', _('Yellow cards')),
        ('red_cards', _('Red cards')),
        ('saves', _('Saves')),
        ('bonus', _('Bonus')),
        ('bps', _('Bonus Points System')),
        ('influence', _('Influence')),
        ('creativity', _('Creativity')),
        ('threat', _('Threat')),
        ('ict_index', _('ICT Index')),
        ('clearances_blocks_interceptions', _('Clearances, blocks and interceptions')),
        ('recoveries', _('Recoveries')),
        ('tackles', _('Tackles')),
        ('defensive_contribution', _('Defensive Contribution')),
        ('starts', _('Game(s) Started')),
        ('expected_goals', _('Expected Goals')),
        ('expected_assists', _('Expected Assists')),
        ('expected_goal_involvements', _('Expected Goal Involvements')),
        ('expected_goals_conceded', _('Expected Goals Conceded')),
    ]
}
