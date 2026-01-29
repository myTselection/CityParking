[![HACS Default](https://img.shields.io/badge/HACS-Default-blue.svg)](https://github.com/hacs/default)
[![GitHub release](https://img.shields.io/github/release/myTselection/CityParking.svg)](https://github.com/myTselection/CityParking/releases)
![GitHub repo size](https://img.shields.io/github/repo-size/myTselection/CityParking.svg)

[![GitHub issues](https://img.shields.io/github/issues/myTselection/CityParking.svg)](https://github.com/myTselection/CityParking/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/myTselection/CityParking.svg)](https://github.com/myTselection/CityParking/commits/master)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/myTselection/CityParking.svg)](https://github.com/myTselection/CityParking/graphs/commit-activity)

# 🅿️ City Parking Home Assistant integration
Home Assistant custom component to provide public city parking information for a desired location. This custom component has been built from the ground up to bring public site data to fetch local parking information and integrate this information into Home Assistant. This integration is built against the public websites provided by seety.co (and maybe other similar sites in future). Sensors will be created for any desired location and specific service can be called to get parking information ad hoc of any location. 

This integration is in no way affiliated with seety.

| :warning: Please don't report issues with this integration to other platforms, they will not be able to support you. |
| ---------------------------------------------------------------------------------------------------------------------|


<p align="center"><img src="https://raw.githubusercontent.com/myTselection/CityParking/master/icon.png"/></p>

# Main use case:

Whenever you exit your car (and while not at home), check if any parking and parking card limitations apply for your current location. Warn you when you need to place your parking card or show local parking rates and cheapest free parking in neighbourhood.

To detect exiting a car, an automation can be defined using sensor.smartphone_ha_activity changing from 'Automotive', or an iOS shortcut can be used to trigger when CarPlay is disconnected and a webhook request can be launched to Home Assistant to trigger an action.







## Installation
- [HACS](https://hacs.xyz/): search for Carbu in the default HACS repo list or use below button to navigate directly to it on your local system and install via HACS. 
   -    [![Open your Home Assistant instance and open the repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg?style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=myTselection&repository=CityParking&category=integration)
- Restart Home Assistant
- Add 'City Parking' integration via HA Settings > 'Devices and Services' > 'Integrations'


# UNDER CONSTRUCTION

## Integration

### Sensors
- <code>sensor.parking_[origin]</code>: sensor with public parking info at location of `origin`
- sensor data will be updated every 5min, unless the coordinates of the origin didn't change
- <details><summary>Sensor attributes</summary>

    | Attribute | Description |
    | --------- | ----------- |
    | State       | **zone** |
    | `origin`    | Original origin provided during setup of the sensor |
    | `latitude`  | Latitude of the origin |
    | `longitude` | Longitude of the origin |
    | `type`      | Type of the public parking, eg paid |
    | `time restrictions`    | Time restrictions for the public parking |
    | `days restrictions`  | Days at which the public parking is limited |
    | `prices`    | Price for 1 or 2 hours parking |
    | `remarkds`  | Extra info related to the public parking |
    | `maxStay`   | Max time you can stay at the public parking |
    | `zone`      | Name of the zone, blue/orange/red zone indication of public parking |
    | `address`   | Address for which the parking information is shown |
    
    </details>
    
### Services / Actions
* Find the public parking information to a given location.
   * ![Service find nearest](https://github.com/myTselection/CityParking/blob/b5ee28f8f46687bad39e5207f400f77a8001bdc7/service_find_nearest.png)
   * <details><summary>It will return a JSON such as example below:</summary>

      ```
      
      city_parking_info:
        user:
          user:
            verified: false
            cars: []
            mustSendMailOnEachTransaction: true
            proAccountActivated: false
            subscribedToOnboardingCampaign: true
            time: "2026-01-28T22:03:31.214000+00:00"
            lastSeen: "2026-01-28T22:03:31.214000+00:00"
            confidence: 0
            lang: en
          lastMapUpdate: "2024-11-20T23:00:00"
          remoteConfigsLastUpdate:
            messages: "2025-01-16"
          access_token: >-
            eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.IjAxNDY3OGEyZTUxMmQ2NDUwMmU4YmI4NWUxZjY1MDdkNjFmMDA3MGNmZWQ3ZDVjM2NhNDYxNGM4ZmYxOGE2YmEi.Rcn09l2bLimX0tpc9DueLAsNQiR0lH3F8RSdlZIh7yk
          expires_in: 10800
          refresh_token: >-
            eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.ImM1MzQ5YjMyNThlYWIwZWZhNWM3ZDlhYjcyZDI2YjIxM2Q5ODQ3YzRiZjYyNGU0MDdjOGE1ODE1NDNiNWU0ZmFhN2RlYzBiZWEzODMyZmY2YTJkNTAyNTE3OTU0YTYxOGQzMWZjMTBmMmM3MmVlMmJkNjQ1NTg1YzFmZjdiZjQ2Ig.QyjbBBgGTGkOR3LtRmXq5m3Ztd1ZHleukI9fFvCKMpQ
          status: OK
        location:
          status: OK
          results:
            - formatted_address: Raadhuisstraat 11, 1016 DB Amsterdam
              countryCode: NL
              geometry:
                location:
                  lat: 52.37315
                  lng: 4.890025
              types:
                - street_address
        rules:
          rules:
            days:
              - 0
              - 1
              - 2
              - 3
              - 4
              - 5
              - 6
            prices:
              "0": 0
              "1": 1.7
              "2": 3.3
            hours:
              - "00:00"
              - "06:00"
            type: paid
            paymentPartner: shpv
            advantageInApp: false
            displayNotPayable: false
            overrides: {}
            forceDisplayPriceTables: false
          risk: 0
          overrides: {}
          properties:
            type: orange-1
            color: "#ff6a00"
            dotted: false
            closest:
              - 4.89029214636468
              - 52.37323057359693
            closestDist: 0.010858118135837055
            maxDistToPay: 0.01
            city: amsterdam
          twoSided: false
          status: OK
        streetComplete:
          rules:
            yellow:
              weight: 4.2
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 1.7
                  "2": 3.3
                hours:
                  - "09:00"
                  - "19:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "600"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone
              table:
                - rows:
                    09:00,19:00:
                      - 0.4
                      - 0.9
                      - 1.7
                      - 3.4
                      - 5.2
                      - 6.9
                      - 8.6
                      - 10.3
                      - 10.3
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "600"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-4:
              weight: 4.2
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 6.7
                  "2": 13.5
                hours:
                  - "09:00"
                  - "24:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "600"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 4
              table:
                - rows:
                    09:00,19:00:
                      - 0.4
                      - 0.9
                      - 1.7
                      - 3.4
                      - 5.2
                      - 6.9
                      - 8.6
                      - 10.3
                      - 10.3
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "600"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
                - rows:
                    09:00,19:00:
                      - 0.4
                      - 0.9
                      - 1.7
                      - 3.4
                      - 5.2
                      - 6.9
                      - 8.6
                      - 10.3
                      - 10.3
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "600"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-2:
              weight: 4.2
              summary:
                days:
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 2.9
                  "2": 5.8
                hours:
                  - "09:00"
                  - "19:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "600"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 2
              table:
                - rows:
                    09:00,19:00:
                      - 0.8
                      - 1.5
                      - 3
                      - 6
                      - 9
                      - 12
                      - 15.1
                      - 18
                      - 18
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "600"
                  days:
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-10:
              weight: 4.2
              summary:
                days:
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 1.2
                  "2": 2.5
                hours:
                  - "10:00"
                  - "20:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "600"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 10
              table:
                - rows:
                    09:00,19:00:
                      - 0.1
                      - 0.1
                      - 0.2
                      - 0.3
                      - 2
                      - 3.7
                      - 5.5
                      - 7.2
                      - 8.9
                      - 10.3
                      - 10.3
                  cols:
                    - "15"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "540"
                    - "600"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            orange-3:
              weight: 5.3
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 5.2
                  "2": 10.4
                hours:
                  - "00:00"
                  - "24:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "1440"
              color:
                color: "#ff6a00"
                dotted: false
              name: Orange zone 3
              table:
                - rows:
                    19:00,24:00:
                      - 0.4
                      - 0.9
                      - 1.7
                      - 3.4
                      - 5.2
                      - 6.8
                      - 10.3
                      - 12
                      - 13.6
                      - 18.9
                      - 20.4
                      - 27.2
                      - 34
                      - 34
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "360"
                    - "420"
                    - "480"
                    - "660"
                    - "720"
                    - "960"
                    - "1260"
                    - "1440"
                  days:
                    - 0
                  accessHours: {}
                  entryHours: null
                - rows:
                    00:00,06:00:
                      - 0.4
                      - 0.9
                      - 1.7
                      - 3.4
                      - 5.2
                      - 6.9
                      - 8.6
                      - 10.3
                      - 12
                      - 13.8
                      - 15.5
                      - 17.2
                      - 18.9
                      - 20.6
                      - 22.4
                      - 24.1
                      - 25.8
                      - 27.5
                      - 29.2
                      - 31
                      - 32.7
                      - 34.4
                      - 36.1
                      - 37.8
                      - 39.6
                      - 41.3
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "540"
                    - "600"
                    - "660"
                    - "720"
                    - "780"
                    - "840"
                    - "900"
                    - "960"
                    - "1020"
                    - "1080"
                    - "1140"
                    - "1200"
                    - "1260"
                    - "1320"
                    - "1380"
                    - "1440"
                  days:
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-16:
              weight: 4.2
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 1.7
                  "2": 2.3
                hours:
                  - "09:00"
                  - "19:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "600"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 16
              table:
                - rows:
                    09:00,19:00:
                      - 1.7
                      - 1.7
                      - 3.4
                      - 5.2
                      - 6.9
                      - 8.6
                      - 10.3
                      - 10.3
                  cols:
                    - "15"
                    - "60"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "600"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
                - rows:
                    09:00,19:00:
                      - 1.7
                      - 1.7
                      - 3.4
                      - 5.2
                      - 6.9
                      - 8.6
                      - 10.3
                      - 10.3
                  cols:
                    - "15"
                    - "60"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "600"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-3:
              weight: 4.2
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 1.7
                  "2": 3.3
                hours:
                  - "09:00"
                  - "19:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "900"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 3
              table:
                - rows:
                    09:00,24:00:
                      - 1.7
                      - 3.5
                      - 7
                      - 14
                      - 20.9
                      - 27.9
                      - 34.9
                      - 41.9
                      - 48.9
                      - 55.8
                      - 62.8
                      - 62.8
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "540"
                    - "900"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
                - rows:
                    09:00,24:00:
                      - 1.7
                      - 3.5
                      - 7
                      - 14
                      - 20.9
                      - 27.9
                      - 34.9
                      - 41.9
                      - 48.9
                      - 55.8
                      - 62.8
                      - 62.8
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "540"
                    - "900"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            orange:
              weight: 5.3
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 7.8
                  "2": 15.5
                hours:
                  - "00:00"
                  - "24:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "900"
              color:
                color: "#ff6a00"
                dotted: false
              name: Orange zone
              table:
                - rows:
                    19:00,24:00:
                      - 21.4
                      - 21.4
                      - 42.8
                      - 64.2
                      - 85.6
                      - 107
                      - 107
                  cols:
                    - "15"
                    - "60"
                    - "360"
                    - "660"
                    - "960"
                    - "1260"
                    - "1440"
                  days:
                    - 0
                  accessHours: {}
                  entryHours: null
                - rows:
                    09:00,24:00:
                      - 1.3
                      - 2.7
                      - 5.4
                      - 10.7
                      - 16.1
                      - 21.5
                      - 26.9
                      - 32.2
                      - 37.6
                      - 43
                      - 48.3
                      - 48.3
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "540"
                    - "900"
                  days:
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            orange-2:
              weight: 5.3
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 6.7
                  "2": 13.5
                hours:
                  - "00:00"
                  - "24:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "720"
              color:
                color: "#ff6a00"
                dotted: false
              name: Orange zone 2
              table:
                - rows:
                    19:00,24:00:
                      - 21.4
                      - 21.4
                      - 42.8
                      - 64.2
                      - 85.6
                      - 107
                      - 107
                  cols:
                    - "15"
                    - "60"
                    - "360"
                    - "660"
                    - "960"
                    - "1260"
                    - "1440"
                  days:
                    - 0
                  accessHours: {}
                  entryHours: null
                - rows:
                    09:00,21:00:
                      - 1.3
                      - 2.7
                      - 5.4
                      - 10.7
                      - 16.1
                      - 21.5
                      - 26.9
                      - 32.2
                      - 37.6
                      - 38.6
                      - 38.6
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "720"
                  days:
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-7:
              weight: 4.2
              summary:
                days:
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 5.2
                  "2": 10.4
                hours:
                  - "09:00"
                  - "19:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "600"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 7
              table:
                - rows:
                    09:00,19:00:
                      - 1.3
                      - 2.7
                      - 5.4
                      - 10.7
                      - 16.1
                      - 21.5
                      - 26.9
                      - 32.2
                      - 32.2
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "600"
                  days:
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-6:
              weight: 4.2
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 6.7
                  "2": 13.5
                hours:
                  - "09:00"
                  - "24:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "900"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 6
              table:
                - rows:
                    09:00,24:00:
                      - 1.7
                      - 3.5
                      - 7
                      - 14
                      - 20.9
                      - 27.9
                      - 34.9
                      - 41.9
                      - 48.9
                      - 55.8
                      - 62.8
                      - 62.8
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "540"
                    - "900"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-12:
              weight: 4.2
              summary:
                days:
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 2.9
                  "2": 5.8
                hours:
                  - "09:00"
                  - "21:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "900"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 12
              table:
                - rows:
                    09:00,24:00:
                      - 0.8
                      - 1.5
                      - 3
                      - 6
                      - 9
                      - 12
                      - 15.1
                      - 18.1
                      - 21.1
                      - 24.1
                      - 27
                      - 27
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "540"
                    - "900"
                  days:
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            noparking:
              weight: 0
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                hours:
                  - "00:00"
                  - "24:00"
                type: noparking
                paymentPartner: null
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks: []
              specialPermits:
                residents: []
                disabled: []
              maxStay: 0
              color:
                color: "#000000"
                dotted: true
              name: Black dotted zone
              table:
                - rows:
                    00:00,24:00: []
                  cols: []
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders: []
              displayNotPayable: false
            yellow-11:
              weight: 4.2
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 0.1
                  "2": 0.2
                hours:
                  - "09:00"
                  - "19:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "720"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 11
              table:
                - rows:
                    09:00,21:00:
                      - 0.8
                      - 1.5
                      - 3
                      - 6
                      - 9
                      - 12
                      - 15.1
                      - 18.1
                      - 21.1
                      - 21.6
                      - 21.6
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "720"
                  days:
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-8:
              weight: 4.2
              summary:
                days:
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 4
                  "2": 8.1
                hours:
                  - "09:00"
                  - "21:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "600"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 8
              table:
                - rows:
                    09:00,19:00:
                      - 1.7
                      - 3.5
                      - 7
                      - 14
                      - 20.9
                      - 27.9
                      - 34.9
                      - 41.8
                      - 41.8
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "600"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            orange-1:
              weight: 5.3
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 1.7
                  "2": 3.3
                hours:
                  - "00:00"
                  - "06:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "1440"
              color:
                color: "#ff6a00"
                dotted: false
              name: Orange zone 1
              table:
                - rows:
                    00:00,24:00:
                      - 2
                      - 4
                      - 8.1
                      - 16.1
                      - 24.2
                      - 32.2
                      - 40.3
                      - 48.3
                      - 56.4
                      - 64.4
                      - 72.5
                      - 80.5
                      - 88.6
                      - 96.6
                      - 104.7
                      - 112.7
                      - 120.8
                      - 128.8
                      - 136.9
                      - 144.9
                      - 153
                      - 161
                      - 169.1
                      - 177.1
                      - 185.2
                      - 193.2
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "540"
                    - "600"
                    - "660"
                    - "720"
                    - "780"
                    - "840"
                    - "900"
                    - "960"
                    - "1020"
                    - "1080"
                    - "1140"
                    - "1200"
                    - "1260"
                    - "1320"
                    - "1380"
                    - "1440"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            orange-4:
              weight: 5.3
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 7.8
                  "2": 9.8
                hours:
                  - "02:00"
                  - "06:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "1440"
              color:
                color: "#ff6a00"
                dotted: false
              name: Orange zone 4
              table:
                - rows:
                    00:00,24:00:
                      - 1.7
                      - 3.5
                      - 7
                      - 14
                      - 20.9
                      - 27.9
                      - 34.9
                      - 41.9
                      - 48.9
                      - 55.8
                      - 62.8
                      - 69.8
                      - 76.8
                      - 83.8
                      - 90.7
                      - 97.7
                      - 104.7
                      - 111.7
                      - 118.7
                      - 125.6
                      - 132.6
                      - 139.6
                      - 146.6
                      - 153.6
                      - 160.5
                      - 167.5
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "540"
                    - "600"
                    - "660"
                    - "720"
                    - "780"
                    - "840"
                    - "900"
                    - "960"
                    - "1020"
                    - "1080"
                    - "1140"
                    - "1200"
                    - "1260"
                    - "1320"
                    - "1380"
                    - "1440"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            orange-5:
              weight: 5.3
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 5.4
                  "2": 10.7
                hours:
                  - "00:00"
                  - "24:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "1440"
              color:
                color: "#ff6a00"
                dotted: false
              name: Orange zone 5
              table:
                - rows:
                    00:00,24:00:
                      - 1.3
                      - 2.7
                      - 5.4
                      - 10.7
                      - 16.1
                      - 21.5
                      - 26.9
                      - 32.2
                      - 37.6
                      - 43
                      - 48.3
                      - 53.7
                      - 59.1
                      - 64.4
                      - 69.8
                      - 75.2
                      - 80.6
                      - 85.9
                      - 91.3
                      - 96.7
                      - 102
                      - 107.4
                      - 112.8
                      - 118.1
                      - 123.5
                      - 128.9
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "540"
                    - "600"
                    - "660"
                    - "720"
                    - "780"
                    - "840"
                    - "900"
                    - "960"
                    - "1020"
                    - "1080"
                    - "1140"
                    - "1200"
                    - "1260"
                    - "1320"
                    - "1380"
                    - "1440"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
                - rows:
                    00:00,24:00:
                      - 1.3
                      - 2.7
                      - 5.4
                      - 10.7
                      - 16.1
                      - 21.5
                      - 26.9
                      - 32.2
                      - 37.6
                      - 43
                      - 48.3
                      - 53.7
                      - 59.1
                      - 64.4
                      - 69.8
                      - 75.2
                      - 80.6
                      - 85.9
                      - 91.3
                      - 96.7
                      - 102
                      - 107.4
                      - 112.8
                      - 118.1
                      - 123.5
                      - 128.9
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "540"
                    - "600"
                    - "660"
                    - "720"
                    - "780"
                    - "840"
                    - "900"
                    - "960"
                    - "1020"
                    - "1080"
                    - "1140"
                    - "1200"
                    - "1260"
                    - "1320"
                    - "1380"
                    - "1440"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-15:
              weight: 4.2
              summary:
                days:
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 2.9
                  "2": 5.8
                hours:
                  - "09:00"
                  - "19:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "720"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 15
              table:
                - rows:
                    09:00,21:00:
                      - 1
                      - 2.1
                      - 4.2
                      - 8.4
                      - 12.6
                      - 16.8
                      - 20.9
                      - 25.1
                      - 29.3
                      - 30.1
                      - 30.1
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "720"
                  days:
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-1:
              weight: 4.2
              summary:
                days:
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 4
                  "2": 8.1
                hours:
                  - "09:00"
                  - "19:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "600"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 1
              table:
                - rows:
                    09:00,19:00:
                      - 1
                      - 2.1
                      - 4.2
                      - 8.4
                      - 12.6
                      - 16.8
                      - 20.9
                      - 25.1
                      - 25.1
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "600"
                  days:
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-13:
              weight: 4.2
              summary:
                days:
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 2.9
                  "2": 5.8
                hours:
                  - "09:00"
                  - "24:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "900"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 13
              table:
                - rows:
                    12:00,24:00:
                      - 1
                      - 2.1
                      - 4.2
                      - 8.4
                      - 12.6
                      - 16.8
                      - 20.9
                      - 25.1
                      - 29.3
                      - 30.1
                      - 30.1
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "720"
                  days:
                    - 0
                  accessHours: {}
                  entryHours: null
                - rows:
                    09:00,24:00:
                      - 1
                      - 2.1
                      - 4.2
                      - 8.4
                      - 12.6
                      - 16.8
                      - 20.9
                      - 25.1
                      - 29.3
                      - 33.5
                      - 37.7
                      - 37.7
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "540"
                    - "900"
                  days:
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            red:
              weight: 6.2
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 5.2
                  "2": 10.4
                hours:
                  - "09:00"
                  - "24:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "600"
              color:
                color: "#ff0000"
                dotted: false
              name: Red zone
              table:
                - rows:
                    09:00,19:00:
                      - 25.1
                      - 25.1
                      - 25.1
                  cols:
                    - "15"
                    - "60"
                    - "600"
                  days:
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-14:
              weight: 4.2
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 4
                  "2": 8.1
                hours:
                  - "09:00"
                  - "24:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "600"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 14
              table:
                - rows:
                    09:00,19:00:
                      - 0.8
                      - 1.5
                      - 3
                      - 6
                      - 9
                      - 12
                      - 15.1
                      - 18
                      - 18
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "600"
                  days:
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-5:
              weight: 4.2
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 1.7
                  "2": 3.3
                hours:
                  - "09:00"
                  - "21:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "720"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 5
              table:
                - rows:
                    09:00,21:00:
                      - 0.4
                      - 0.9
                      - 1.7
                      - 3.4
                      - 5.2
                      - 6.9
                      - 8.6
                      - 10.3
                      - 12
                      - 12.3
                      - 12.3
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "720"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
                - rows:
                    09:00,21:00:
                      - 0.4
                      - 0.9
                      - 1.7
                      - 3.4
                      - 5.2
                      - 6.9
                      - 8.6
                      - 10.3
                      - 12
                      - 12.3
                      - 12.3
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "480"
                    - "720"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            yellow-9:
              weight: 4.2
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 6.7
                  "2": 13.5
                hours:
                  - "09:00"
                  - "19:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "600"
              color:
                color: "#ffdd00"
                dotted: false
              name: Yellow zone 9
              table:
                - rows:
                    10:00,20:00:
                      - 0.3
                      - 0.6
                      - 1.3
                      - 2.6
                      - 3.9
                      - 5.2
                      - 6.5
                      - 7.7
                      - 8.1
                      - 8.1
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "600"
                  days:
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                  accessHours: {}
                  entryHours: null
                - rows:
                    10:00,17:00:
                      - 0.3
                      - 0.6
                      - 1.3
                      - 2.6
                      - 3.9
                      - 5.2
                      - 6.5
                      - 7.7
                      - 8.1
                      - 8.1
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "120"
                    - "180"
                    - "240"
                    - "300"
                    - "360"
                    - "420"
                    - "600"
                  days:
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
            orange-6:
              weight: 5.3
              summary:
                days:
                  - 0
                  - 1
                  - 2
                  - 3
                  - 4
                  - 5
                  - 6
                prices:
                  "0": 0
                  "1": 8.1
                  "2": 10.1
                hours:
                  - "02:00"
                  - "06:00"
                type: paid
                paymentPartner: shpv
                advantageInApp: false
                displayNotPayable: false
                overrides: {}
                forceDisplayPriceTables: false
              remarks:
                - "Fine: 150€."
              specialPermits:
                residents: []
                disabled: []
              maxStay: "1440"
              color:
                color: "#ff6a00"
                dotted: false
              name: Orange zone 6
              table:
                - rows:
                    02:00,06:00:
                      - 2
                      - 4
                      - 8.1
                      - 16.1
                      - 24.2
                      - 32.2
                      - 40.3
                      - 48.3
                      - 48.3
                  cols:
                    - "15"
                    - "30"
                    - "60"
                    - "300"
                    - "540"
                    - "780"
                    - "1020"
                    - "1260"
                    - "1440"
                  days:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  accessHours: {}
                  entryHours: null
              parkingPaymentProviders:
                - seety_nl
                - 4411_nl
                - driveulu_nl
                - ease2pay_nl
                - easypark_nl
                - lekkerparkeren_nl
                - mkbbrandstof_nl
                - parkd_nl
                - parkline_nl
                - parkmobile_nl
                - parksen_nl
                - paybyphone_nl
                - qpark_nl
                - sms_parking_nl
                - tanqyou_nl
                - yellowbrick_nl
              displayNotPayable: false
          table:
            - rows:
                00:00,24:00:
                  - 2
                  - 4
                  - 8.1
                  - 16.1
                  - 24.2
                  - 32.2
                  - 40.3
                  - 48.3
                  - 56.4
                  - 64.4
                  - 72.5
                  - 80.5
                  - 88.6
                  - 96.6
                  - 104.7
                  - 112.7
                  - 120.8
                  - 128.8
                  - 136.9
                  - 144.9
                  - 153
                  - 161
                  - 169.1
                  - 177.1
                  - 185.2
                  - 193.2
              cols:
                - "15"
                - "30"
                - "60"
                - "120"
                - "180"
                - "240"
                - "300"
                - "360"
                - "420"
                - "480"
                - "540"
                - "600"
                - "660"
                - "720"
                - "780"
                - "840"
                - "900"
                - "960"
                - "1020"
                - "1080"
                - "1140"
                - "1200"
                - "1260"
                - "1320"
                - "1380"
                - "1440"
              days:
                - 0
                - 1
                - 2
                - 3
                - 4
                - 5
                - 6
              accessHours: {}
              entryHours: null
          maxStay: "1440"
          remarks:
            - "Fine: 150€."
          specialPermits:
            residents: []
            disabled: []
          providers:
            - descriptionApp: null
              descriptionSMS: null
              fees:
                registration:
                  fixed: 0
                session:
                  comment: null
                  fixed: 0.35
                  percentage: null
                sessionSubscription: null
                notifSms:
                  comment: null
                  fixed: 0.15
                  percentage: null
                notifApp: null
              advantageApp:
                fr:
                  - >-
                    Il n'est pas nécessaire de sélectionner une durée spécifique
                    (start & stop)
                  - Disponible dans plus de 150 villes belges
                  - Inscription plutôt facile
                en:
                  - Not necessary to select a specific duration (start & stop)
                  - Available in more than 60 Belgian cities
                  - Registration rather  easy
                nl:
                  - >-
                    Het is niet nodig om een specifieke duur te selecteren (start &
                    stop)
                  - Beschikbaar in meer dan 60 Belgische steden
                  - Inschrijving eerder eenvoudig
              disadvantageApp:
                fr:
                  - Relativement cher
                  - >-
                    Dans certains cas, il faut se rendre à l'horodateur pour avoir le
                    code de la zone
                  - Attention aux notifications payantes
                  - Inscription obligatoire avant de découvrir l'app
                  - Nombre de parkings publics limité
                en:
                  - Relatively expensive
                  - >-
                    In some cases, you have to go to the parcmeter to get the code of
                    the zone
                  - Beware of paid notifications
                  - Registration required before discovering the app
                  - Limited number of public parkings
                nl:
                  - Relatief duur
                  - >-
                    In sommige gevallen moet u naar de parkeermeter gaan om de code
                    voor de zone te krijgen
                  - Pas op voor meldingen die betalend zijn
                  - Inschrijving vereist voor het ontdekken van de app
                  - Beperkt aantal openbare parkings
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: "4411"
              intName: 4411_nl
              rating: 4
              logo: >-
                https://storage.googleapis.com/cpark-static-images/mobility-providers/4411.png
              subscriptions: []
              url: www.4411.io
              transactionPrice: null
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: "0"
              subscriptionType: null
            - descriptionApp: null
              descriptionSMS: null
              fees:
                registration:
                  fixed: 0
                session:
                  comment:
                    fr: Hors TVA
                    en: Exclusive of VAT
                    nl: Exclusief BTW
                  fixed: 0.3
                  percentage: null
                sessionSubscription:
                  comment: null
                  fixed: 0
                  percentage: null
                notifSms:
                  comment: null
                  fixed: 0.25
                  percentage: null
                notifApp: null
              advantageApp:
                fr:
                  - >-
                    Inclus un système de navigation (mais très limité par rapport  à
                    Google maps ou Waze)
                en: []
                nl: []
              disadvantageApp:
                fr:
                  - Inscription obligatoire avant de découvrir l'app
                  - >-
                    Obligation d'avoir une plaque de voiture valide pour accéder à
                    l'application
                  - Relativement cher
                  - Peu d'explications sur le fonctionnement de la carte
                  - Le design et l'expérience utilisateur pourraient être amélioré
                en: []
                nl: []
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: Drive ULU
              intName: driveulu_nl
              rating: 4
              logo: >-
                https://storage.googleapis.com/cpark-static-images/mobility-providers/drive-ulu.jpg
              subscriptions: []
              url: www.driveulu.com
              transactionPrice: null
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: null
              subscriptionType: null
            - descriptionApp: null
              descriptionSMS: null
              fees:
                registration:
                  fixed: 0
                session:
                  comment: null
                  fixed: 0.19
                  percentage: null
                sessionSubscription:
                  comment: null
                  fixed: 0
                  percentage: null
                notifSms:
                  comment:
                    fr: Commentaire en FR
                    en: Commentaire en EN
                    nl: Commentaire en NL
                  fixed: 0
                  percentage: null
                notifApp: null
              advantageApp:
                fr:
                  - Disponible dans plus de 140 villes aux Pays-Bas
                  - Frais de transaction raisonnable si vous  rechargez du crédit
                  - >-
                    Possibilité de payer son parking sans devoir créer de compte (mais
                    dans ce cas les frais de transactions sont beaucoup plus chers
                    (0,35€)
                en: []
                nl: []
              disadvantageApp:
                fr:
                  - Application peu intuitive
                  - >-
                    Si vous n'utilisez par leur système de crédit, les frais de
                    transactions sont très chers (0,25€ avec iDEAL et 0,35€ avec une
                    carte de crédit)
                  - >-
                    Vous devez définir à l'avance combien de temps vous voulez rester
                    stationné
                  - >-
                    Pas d'informations dans les zones où le paiement du parking n'est
                    pas disponible
                en: []
                nl: []
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: Easy2pay
              intName: ease2pay_nl
              rating: 4
              logo: >-
                https://storage.googleapis.com/cpark-static-images/mobility-providers/ease2pay.png
              subscriptions:
                - period: 7
                  price: 0.49
                - period: 30
                  price: 1.49
                - period: 365
                  price: 14.99
              url: http://www.ease2pay.nl/
              transactionPrice: null
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: null
              subscriptionType: null
            - descriptionApp: null
              descriptionSMS: null
              fees:
                registration:
                  fixed: 0
                session:
                  comment:
                    fr: Min. 29cts.
                    en: Min. 29cts.
                    nl: Min. 29cts.
                  fixed: null
                  percentage: 15
                sessionSubscription: null
                notifSms: null
                notifApp: null
              advantageApp:
                fr:
                  - Choix de la zone relativement aisé
                  - Inscription relativement facile
                  - Possibilité de payer son stationnement dans des parking publics
                en: []
                nl: []
              disadvantageApp:
                fr:
                  - Une des applications la plus chère du marché
                  - Attention aux notifications payantes
                  - Obligé de choisir une durée de stationnement prédéfinie
                  - Inscription obligatoire avant de découvrir l'app
                en: []
                nl: []
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: EasyPark
              intName: easypark_nl
              rating: 4
              logo: >-
                https://storage.googleapis.com/cpark-static-images/mobility-providers/easypark.png
              subscriptions:
                - period: 30
                  price: 1.99
              url: www.easyparknederland.nl
              transactionPrice: null
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: null
              subscriptionType: null
            - descriptionApp: null
              descriptionSMS: null
              fees:
                registration:
                  fixed: 0
                session:
                  comment: null
                  fixed: 0.22
                  percentage: null
                sessionSubscription:
                  comment: null
                  fixed: 0
                  percentage: null
                notifSms: null
                notifApp: null
              advantageApp:
                fr:
                  - >-
                    Notifications gratuites pour vous rappelez qu'une session est en
                    cours
                  - Vous pouvez ajouter autant de plaque que vous le désirez
                  - Disponible dans plus de 100 villes aux Pays-bas
                en: []
                nl: []
              disadvantageApp:
                fr:
                  - Frais de transaction relativement cher
                  - Le design et l'expérience utilisateur pourraient être amélioré
                  - Application uniquement disponible aux Pays-Bas
                  - Inscription obligatoire afin de découvrir l'app
                en: []
                nl: []
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: LekkerParkeren
              intName: lekkerparkeren_nl
              rating: 4
              logo: >-
                https://storage.googleapis.com/cpark-static-images/mobility-providers/lekker-parkeren.png
              subscriptions:
                - period: 30
                  price: 1.99
              url: http://www.lekkerparkeren.nl/
              transactionPrice: null
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: null
              subscriptionType: null
            - descriptionApp: null
              descriptionSMS: null
              fees:
                registration:
                  fixed: 0
                session:
                  comment: null
                  fixed: 0
                  percentage: null
                sessionSubscription:
                  comment: null
                  fixed: 0.2
                  percentage: null
                notifSms: null
                notifApp: null
              advantageApp:
                fr:
                  - >-
                    Il est également possible de payer son essence, son carwash et les
                    recharges électriques avec l'application
                  - >-
                    L'app peut être utilisée dans plusieurs pays européens pour le
                    carburant et la recharge electrique (pas le parking)
                en: []
                nl: []
              disadvantageApp:
                fr:
                  - >-
                    App uniquement disponible pour les professionnels avec un
                    abonnement (8,9€/moins) obligatoire
                  - >-
                    L'app est principalement destinée aux payement de carburant ce qui
                    la rend moins pratique pour le parking
                  - Le paiement du parking est uniquement disponible aux Pays-bas
                en: []
                nl: []
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: MKB Brandstof
              intName: mkbbrandstof_nl
              rating: 4
              logo: >-
                https://storage.googleapis.com/cpark-static-images/mobility-providers/mkb-brandstof.png
              subscriptions:
                - period: 30
                  price: 8.9
              url: http://www.mkb-brandstof.nl/
              transactionPrice: null
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: null
              subscriptionType: null
            - descriptionApp: null
              descriptionSMS: null
              fees:
                registration:
                  fixed: 5
                session:
                  comment: null
                  fixed: 0
                  percentage: null
                sessionSubscription:
                  comment: null
                  fixed: 0.15
                  percentage: null
                notifSms:
                  comment: null
                  fixed: 0.25
                  percentage: null
                notifApp: null
              advantageApp:
                fr:
                  - >-
                    Possibilité de payer son parking, son car-wash et son essence avec
                    la même app
                  - Vous pouvez bénéficier d'un account manager dédié
                en: []
                nl: []
              disadvantageApp:
                fr:
                  - L'app est uniquement disponible pour les professionnels
                  - >-
                    Il faut payer en plus pour utiliser l'app pour le carburant et les
                    carwash
                  - >-
                    Obligation de payer les frais d'inscription (5 €) et de souscrire
                    à un abonnement pour  utiliser l'application
                en: []
                nl: []
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: Parkline
              intName: parkline_nl
              rating: 4
              logo: >-
                https://storage.googleapis.com/cpark-static-images/mobility-providers/parkline.png
              subscriptions:
                - period: 30
                  price: 2.5
              url: http://www.parkline.nl/
              transactionPrice: null
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: null
              subscriptionType: null
            - descriptionApp: null
              descriptionSMS: null
              fees:
                registration:
                  fixed: 0
                session:
                  comment: null
                  fixed: 0.39
                  percentage: null
                sessionSubscription:
                  comment: null
                  fixed: 0.15
                  percentage: null
                notifSms:
                  comment: null
                  fixed: 0.25
                  percentage: null
                notifApp: null
              advantageApp:
                fr:
                  - >-
                    Possibilité de payer son stationnement dans certains parking
                    publics
                  - >-
                    Choix de la zone de stationnement en choisissant le code de la
                    zone ou en cliquant sur la carte
                  - Possibilité d'ajouter certaines zones en favoris
                en: []
                nl: []
              disadvantageApp:
                fr:
                  - >-
                    Une des app les plus chère pour payer son stationnement aux
                    Pays-Bas
                  - >-
                    Vous devez payer 1€ chaque fois que vous voulez rajouter une
                    plaque d'immatriculation
                  - Attention aux notifications payantes
                  - Pas de possibilité de bénéficier des tickets gratuits
                  - Application relativement complexe à utiliser
                  - Inscription longue et obligatoire avant de découvrir le service
                  - Nombre de parkings publics limité
                en: []
                nl: []
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: Parkmobile
              intName: parkmobile_nl
              rating: 4
              logo: >-
                https://storage.googleapis.com/cpark-static-images/mobility-providers/parkmobile.png
              subscriptions:
                - period: 30
                  price: 2.5
              url: http://www.parkmobile.nl/
              transactionPrice: null
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: null
              subscriptionType: null
            - descriptionApp: null
              descriptionSMS: null
              fees:
                registration:
                  fixed: 0
                session:
                  comment: null
                  fixed: 0.2
                  percentage: null
                sessionSubscription: null
                notifSms:
                  comment: null
                  fixed: 0.15
                  percentage: null
                notifApp: null
              advantageApp:
                fr:
                  - Inscription relativement facile
                  - Différentes manières de choisir l'horodateur à proximité
                  - Possibilité d'enregistrer une zone en tant que favoris
                  - Frais de transaction raisonnable
                  - Disponible dans 112 villes aux Pays-Bas
                en: []
                nl: []
              disadvantageApp:
                fr:
                  - Inscription obligatoire avant de découvrir l'app
                  - "Application peu intuitive: relativement difficile à utiliser"
                  - >-
                    Uniquement disponible pour le parking de rue (Pas possible de
                    réserver un parking public)
                  - Attention aux notifications payantes
                  - Obligé de choisir une durée de stationnement prédéfinie
                  - >-
                    Certain services encore non disponible aux Pays-Bas comme payer
                    son titre de transport via l'application
                en: []
                nl: []
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: PayByPhone
              intName: paybyphone_nl
              rating: 4
              logo: >-
                https://storage.googleapis.com/cpark-static-images/mobility-providers/paybyphone.png
              subscriptions: []
              url: www.paybyphone.com
              transactionPrice: null
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: null
              subscriptionType: null
            - descriptionApp: null
              descriptionSMS: null
              fees:
                registration:
                  fixed: 0
                session:
                  comment:
                    fr: Hors TVA
                    en: Exclusive of VAT
                    nl: Exclusief BTW
                  fixed: 0.37
                  percentage: null
                sessionSubscription: null
                notifSms: null
                notifApp: null
              advantageApp:
                fr:
                  - >-
                    Possibilité de réserver son stationnement à l'avance dans un
                    parking Q-park
                en: []
                nl: []
              disadvantageApp:
                fr:
                  - >-
                    Une des app les plus chère pour payer son stationnement aux
                    Pays-Bas
                  - >-
                    L'app  est principalement destiné à payer son stationnement dans
                    les parkings Q-park plutôt  qu'en rue.
                  - >-
                    Les fonctionnalités sont  très limitées si on ne crée pas de
                    compte
                en: []
                nl: []
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: QPark
              intName: qpark_nl
              rating: 4
              logo: >-
                https://storage.googleapis.com/cpark-static-images/mobility-providers/qpark.png
              subscriptions: []
              url: http://www.q-park.nl/
              transactionPrice: null
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: null
              subscriptionType: null
            - descriptionApp:
                fr: "<div class=\"prices\">\n        <h3>Tarifs</h3>\n        <ul>\n \t<li>Frais de transaction de 0.15€ (les moins chers)</li>\n\t<li>Frais d'activation : 0€</li>\n\t<li>Frais de notification dans l'app : gratuit </li>\n\t<li>Moyens de paiements acceptés (Carte de crédit, Domiciliation, Apple et Google Pay)</li>\n</ul></div>"
                en: "<div class=\"prices\">\n        <h3>Rates</h3>\n        <ul>\n \t<li>Transaction fee of 0.15€ (least expensive)</li>\n\t<li>Activation fee: 0€</li>\n\t<li>Notification fee in the app: free</li>\n\t<li>Accepted payment methods (Credit Card, domiciliation, Apple and Google Pay)</li>\n</ul></div>"
                nl: "<div class=\"prices\">\n        <h3>Tarieven</h3>\n        <ul>\n \t<li>Transactiekosten van 0.15€ (goedkoopste)</li>\n\t<li>Activeringskosten: 0€</li>\n\t<li>Notificatiekost in de app: gratis</li>\n\t<li>Betaalmiddelen (kredietkaart, domiciliering, Apple en Google Pay)</li>\n</ul></div>"
              descriptionSMS: null
              fees:
                registration:
                  fixed: 0
                session:
                  comment: null
                  fixed: 0.19
                  percentage: null
                sessionSubscription: null
                notifSms: null
                notifApp: null
              advantageApp:
                fr:
                  - >-
                    L'app vous aide à trouver les zones de stationnement gratuites ou
                    les moins chères
                  - Seety est l'app la moins chère pour payer son parking au Pays-Bas
                  - Frais de transaction les plus bas du marché
                  - L'app la plus intuitive (inscription rapide, facile et sécurisée)
                  - Propose automatiquement la zone la plus proche
                  - >-
                    Il n'est pas nécessaire de sélectionner une durée spécifique
                    (start & stop)
                  - >-
                    Notifications intelligentes gratuites pour éviter les mauvaises
                    surprises
                  - Recevez gratuitement une facture mensuelle pour les professionnels
                  - >-
                    Possibilité de réserver un grand nombre de parkings publics via
                    l'app
                  - Disponible partout aux Pays-Bas et en Belgique
                  - Support client 5 étoiles
                en: []
                nl: []
              disadvantageApp:
                fr:
                  - Payement du parking en rue pas encore disponible en France
                en: []
                nl: []
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: Seety
              intName: seety_nl
              rating: 4.9
              logo: https://storage.googleapis.com/cpark-static-images/seety.png
              subscriptions: []
              url: https://seety.page.link/Kdp9
              transactionPrice: "0.15"
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: null
              subscriptionType: null
            - descriptionApp: null
              descriptionSMS: null
              fees:
                registration:
                  fixed: 5
                session:
                  comment: null
                  fixed: 0.3
                  percentage: null
                sessionSubscription:
                  comment: null
                  fixed: 0.16
                  percentage: null
                notifSms:
                  comment: null
                  fixed: 0.3
                  percentage: null
                notifApp: null
              advantageApp:
                fr:
                  - Possibilité de payer son parking par sms
                  - >-
                    Il est également possible de payer son parking dans des parking
                    publics
                en: []
                nl: []
              disadvantageApp:
                fr:
                  - >-
                    Le paiement de  stationnement est assez cher, 0,3€ en plus du prix
                    du parking
                  - >-
                    Même lorsque que vous souscrivez à une abonnement il faut
                    continuer à payer des frais de transaction
                  - L'inscription à l'app est obligatoire et assez fastidieuse
                  - Le design de l'app pourrait être amélioré
                en: []
                nl: []
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: SMS Parking
              intName: sms_parking_nl
              rating: 4
              logo: >-
                https://storage.googleapis.com/cpark-static-images/mobility-providers/sms-parking.png
              subscriptions:
                - period: 30
                  price: 1.85
              url: www.smsparking.nl
              transactionPrice: null
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: null
              subscriptionType: null
            - descriptionApp: null
              descriptionSMS: null
              fees:
                registration:
                  fixed: 0
                session:
                  comment:
                    fr: Flexible
                    en: Flexible
                    nl: Flexibel
                  fixed: 0.2
                  percentage: null
                sessionSubscription:
                  comment: null
                  fixed: 0
                  percentage: null
                notifSms:
                  comment: null
                  fixed: 0.25
                  percentage: null
                notifApp: null
              advantageApp:
                fr:
                  - >-
                    Il est également possible de payer son carburant, les recharges
                    électriques et certaines voitures partagées directement via
                    l'application
                  - Disponible dans plus de 150 villes aux Pays-Bas
                  - Possibilité d'enregistrer des zones en favori
                en: []
                nl: []
              disadvantageApp:
                fr:
                  - Inscription obligatoire afin de découvrir l'app
                  - "Application peu intuitive: relativement difficile à utiliser"
                  - >-
                    L'app est principalement destinée aux payement de carburant ce qui
                    la rend moins pratique pour le parking
                  - >-
                    Vous devez définir à l'avance combien de temps vous voulez rester
                    stationné
                  - Uniquement disponible aux Pays-Bas
                en: []
                nl: []
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: TanQyou
              intName: tanqyou_nl
              rating: 4
              logo: >-
                https://storage.googleapis.com/cpark-static-images/mobility-providers/tanqyou.png
              subscriptions:
                - period: 30
                  price: 1.5
              url: www.tanqyou.com
              transactionPrice: null
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: null
              subscriptionType: null
            - descriptionApp: null
              descriptionSMS: null
              fees:
                registration:
                  fixed: 5
                session:
                  comment: null
                  fixed: 0.34
                  percentage: null
                sessionSubscription:
                  comment:
                    fr: Abonnement flex. Min 0,15€, max 0,50€.
                    en: Flex subscription. Min 0,15€, max 0,50€.
                    nl: Flex abonnement. Min 0,15€, max 0,50€.
                  fixed: 0.15
                  percentage: null
                notifSms:
                  comment: null
                  fixed: 0.35
                  percentage: null
                notifApp: null
              advantageApp:
                fr:
                  - Possibilité d'ajouter certaines zones en favoris
                  - Présentation des différents horodateurs à proximité
                en: []
                nl: []
              disadvantageApp:
                fr:
                  - >-
                    Vous devez payer 2,5€ chaque fois que vous voulez rajouter une
                    plaque d'immatriculation
                  - Une des applications la plus chère du marché
                  - Inscription obligatoire avant de découvrir l'app
                  - Uniquement disponible pour le parking en rue
                  - Inscription relativement longue
                en: []
                nl: []
              advantageSms:
                fr: []
                en: []
                nl: []
              disadvantageSms:
                fr: []
                en: []
                nl: []
              name: Yellowbrick
              intName: yellowbrick_nl
              rating: 4
              logo: >-
                https://storage.googleapis.com/cpark-static-images/mobility-providers/yellowbrick.png
              subscriptions:
                - period: 7
                  price: 0.75
              url: https://www.yellowbrick.nl/
              transactionPrice: null
              notificationPrice: "0"
              registrationFees: "0"
              subscriptionPrice: null
              subscriptionType: null
          city:
            fr: Amsterdam
            en: Amsterdam
            nl: Amsterdam
          cityName: Amsterdam
          status: OK
        origin: zone.home
        origin_coordinates:
          lat: 52.3731339
          lon: 4.8903147
          bounds: {}
        extra_data:
          origin: zone.home
          latitude: 52.3731339
          longitude: 4.8903147
          type: paid
          time_restrictions:
            - "00:00"
            - "06:00"
          days_restrictions: 7d/7
          prices: 1.7€ (1h) - 3.3€ (2h)
          remarks: "Fine: 150€."
          maxStay: 24h
          zone: orange-1
          address: Raadhuisstraat 11, 1016 DB Amsterdam, NL

      
      ```

</details>



## Status
Proof of concept status, still validating and extending functionalities. [Issues](https://github.com/myTselection/CityParking/issues) section in GitHub.

## Technical pointers
The main logic and API connection related code can be found within source code CityParking/custom_components/cityparking:
- [sensor.py](https://github.com/myTselection/CityParking/blob/master/custom_components/cityparking/sensor.py)
- [coordinator.py](https://github.com/myTselection/CityParking/blob/master/custom_components/cityparking/coordinator.py)
- [seetyApi SeetyAPI](https://github.com/myTselection/CityParking/blob/master/custom_components/cityparking/seetyApi/__init__.py)

All other files just contain boilerplat code for the integration to work wtihin HA or to have some constants/strings/translations.

If you would encounter some issues with this custom component, you can enable extra debug logging by adding below into your `configuration.yaml`:
```
logger:
  default: info
  logs:
     custom_components.cityparking: debug
```

## Example usage: TODO

