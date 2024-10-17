# Property Map Web Application

This web application visualizes property data on an interactive map and provides functionality to view historical price data for individual properties.

## Features

- Interactive map displaying property locations
- Color-coded markers based on gross rental yield
- Popup information for each property
- Historical price data retrieval for individual properties

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/drivenone/Property-Map-WebApp.git
   cd property-map-webapp
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a file named `TOKEN` in the project root directory and add your Brightdata API token to it.

5. Ensure you have a CSV file named `zillow_memphistn.csv` in the project root directory with the required property data.

## Usage

1. Run the Flask application:
   ```
   python app.py
   ```

2. Open a web browser and navigate to `http://localhost:5000`

3. The interactive map will be displayed with property markers. Click on a marker to view property details and access the price history feature.

## File Structure

- `app.py`: Main application file containing the Flask routes and map generation logic
- `requirements.txt`: List of Python package dependencies
- `TOKEN`: File containing the Brightdata API token (not included in the repository)
- `zillow_memphistn.csv`: CSV file containing property data (not included in the repository)
- `templates/`: Directory containing HTML templates
  - `properties_map.html`: Template for the main map view
  - `price_history.html`: Template for displaying price history

## Contributing

Contributions to this project are welcome. Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Folium](https://python-visualization.github.io/folium/) for map visualization
- [Brightdata](https://brightdata.com/) for providing historical price data
