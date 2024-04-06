# Mt Fromme Gate Closing Time Home Assistant Sensor

Integrate the Mt Fromme gate closing times into Home Assistant with this custom sensor.

## Installation

1. **Get the script**: Clone this repo and place `fromme.py` in your Home Assistant's scripts directory.
2. **Configure Home Assistant**:
   *Add this to your configuration.yaml file, replacing path/to for your specific use*
   ```yaml
   command_line:
     - sensor:
       name: mt_fromme_gate_closing_time
       command: "python3 /path/to/fromme.py"
       scan_interval: 86400
4. Restart Home Assistant to apply the changes.

## Post-Installation

Once installed, you can add the sensor to your Home Assistant dashboard to monitor the Mt Fromme gate closing times conveniently from your home screen.

![Sensor Card](https://images2.imgbox.com/29/a7/Fi85HIVc_o.png)

![Example](https://images2.imgbox.com/ad/09/DVDFeLtb_o.png)

## Features

- **Automatic Updates**: The sensor fetches and updates the gate closing times for Mt Fromme from the official website once per day.
- **Home Assistant Integration**: Seamlessly integrates into Home Assistant as a command-line sensor, displaying the current gate closing time.
- **Easy Configuration**: Simple setup with a single entry in the `configuration.yaml` file of Home Assistant.

## Risks
As this is just a simple web scraper, and the DNV chooses to not make it easy to scrape their data, this plugin may break if they update their page layout.

## Contributing
Feel free to fork the project, make improvements, and submit pull requests.

## License
Distributed under the MIT License. See 'LICENSE' for more information.
