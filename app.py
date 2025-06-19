"""
Flask Web Application for Cascadia Watershed Lookup

A web service that accepts street addresses and returns detailed watershed
information for locations within the Cascadia bioregion.
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from watershed_lookup import CascadiaWatershedLookup
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize watershed lookup service
watershed_service = None

def init_watershed_service():
    """Initialize the watershed lookup service with proper error handling."""
    global watershed_service
    try:
        watershed_data_path = os.environ.get('WATERSHED_DATA_PATH', 'data/cascadia_watersheds.gpkg')
        watershed_service = CascadiaWatershedLookup(watershed_data_path)
        logger.info("Watershed lookup service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize watershed service: {e}")
        watershed_service = None

# Initialize service on startup
init_watershed_service()

@app.route('/')
def index():
    """Serve the main web interface."""
    google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('index.html', google_maps_api_key=google_maps_api_key)

@app.route('/api/lookup', methods=['POST'])
def api_lookup():
    """
    API endpoint for watershed lookup.
    
    Expects JSON payload with 'address' field.
    Returns watershed information or error.
    """
    try:
        # Check if service is available
        if watershed_service is None:
            return jsonify({
                'error': 'Watershed service unavailable',
                'message': 'The watershed dataset is not loaded. Please check the data setup.'
            }), 503
        
        # Get request data
        data = request.get_json()
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Please provide an address in the request body'
            }), 400
        
        address = data['address'].strip()
        if not address:
            return jsonify({
                'error': 'Empty address',
                'message': 'Please provide a valid street address'
            }), 400
        
        # Get Google Maps API key from environment  
        google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        
        # Perform watershed lookup
        logger.info(f"Looking up watershed for address: {address}")
        result = watershed_service.lookup_watershed(address, google_maps_api_key)
        
        if result:
            logger.info(f"Successfully found watershed for: {address}")
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            logger.warning(f"No watershed found for address: {address}")
            return jsonify({
                'error': 'Watershed not found',
                'message': 'No watershed information found for this address. It may be outside the Cascadia bioregion or the address could not be geocoded.'
            }), 404
    
    except Exception as e:
        logger.error(f"Error in watershed lookup: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred while processing your request'
        }), 500

@app.route('/api/lookup-with-validation', methods=['POST'])
def api_lookup_with_validation():
    """
    Enhanced API endpoint for watershed lookup with address validation and suggestions.
    
    Supports both single-line and multi-line address formats.
    Returns validation results and suggestions for invalid addresses.
    """
    try:
        # Check if service is available
        if watershed_service is None:
            return jsonify({
                'error': 'Watershed service unavailable',
                'message': 'The watershed dataset is not loaded. Please check the data setup.'
            }), 503
        
        # Get request data
        data = request.get_json()
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Please provide an address in the request body'
            }), 400
        
        address_input = data['address']
        if not address_input or not address_input.strip():
            return jsonify({
                'error': 'Empty address',
                'message': 'Please provide a valid address'
            }), 400
        
        # Get Google Maps API key from environment  
        google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        
        # Perform enhanced watershed lookup with validation
        logger.info(f"Looking up watershed with validation for: {address_input[:50]}...")
        result = watershed_service.lookup_watershed_with_validation(address_input, google_maps_api_key)
        
        if result["success"]:
            logger.info(f"Successfully found watershed with validation")
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            # Address validation failed or no watershed found
            logger.warning(f"Validation failed or no watershed found")
            
            # If we have suggestions, return them with a 422 status (validation error)
            if result["validation"]["suggestions"]:
                return jsonify({
                    'success': False,
                    'validation_error': True,
                    'data': result,
                    'message': 'Address could not be validated. Please try one of the suggested addresses.'
                }), 422
            else:
                return jsonify({
                    'success': False,
                    'data': result,
                    'message': 'Address could not be geocoded or is outside the Cascadia bioregion.'
                }), 404
    
    except Exception as e:
        logger.error(f"Error in enhanced watershed lookup: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred while processing your request'
        }), 500

@app.route('/api/validate-address', methods=['POST'])
def api_validate_address():
    """
    API endpoint for address validation only (without watershed lookup).
    
    Useful for form validation and address correction.
    """
    try:
        # Check if service is available
        if watershed_service is None:
            return jsonify({
                'error': 'Watershed service unavailable',
                'message': 'The watershed dataset is not loaded. Please check the data setup.'
            }), 503
        
        # Get request data
        data = request.get_json()
        if not data or 'address' not in data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Please provide an address in the request body'
            }), 400
        
        address_input = data['address']
        if not address_input or not address_input.strip():
            return jsonify({
                'error': 'Empty address', 
                'message': 'Please provide a valid address'
            }), 400
        
        # Get Google Maps API key from environment  
        google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        
        # Parse and validate the address
        parsed_address = watershed_service.parse_address_input(address_input)
        validation_result = watershed_service.validate_and_suggest_address(parsed_address, google_maps_api_key)
        
        response_data = {
            'input_address': address_input,
            'parsed_address': parsed_address,
            'validation': validation_result
        }
        
        if validation_result["is_valid"]:
            return jsonify({
                'success': True,
                'data': response_data
            })
        else:
            return jsonify({
                'success': False,
                'data': response_data,
                'message': 'Address validation failed. Check suggestions for alternatives.'
            }), 422
    
    except Exception as e:
        logger.error(f"Error in address validation: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred while processing your request'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    service_status = 'available' if watershed_service is not None else 'unavailable'
    
    return jsonify({
        'status': 'healthy',
        'service': service_status,
        'version': '1.0.0'
    })

@app.route('/favicon.ico')
def favicon():
    """Serve favicon."""
    return send_from_directory(os.path.join(app.root_path, 'static'), 
                              'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    # Development server configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Cascadia Watershed Lookup service on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )