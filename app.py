from flask import Flask, render_template, request, jsonify
import sys

app = Flask(__name__)


def calculate_warmup_weights(target_weight):
    """
    Calculate warmup weights at 45%, 65%, and 85% of target weight.
    
    Args:
        target_weight: The target weight (in kg)
    
    Returns:
        A tuple of (weight_45%, weight_65%, weight_85%) rounded to nearest 5kg
    """
    weight_45 = round(target_weight * 0.45 / 5) * 5
    weight_65 = round(target_weight * 0.65 / 5) * 5
    weight_85 = round(target_weight * 0.85 / 5) * 5
    
    return weight_45, weight_65, weight_85


def plate_weight(total_weight, bar_weight=20):
    """
    Calculate the weight to load on each side of the barbell.
    
    Args:
        total_weight: The total weight to be lifted (in kg)
        bar_weight: The weight of the barbell (default is 20kg)
    
    Returns:
        The weight to load on each side of the barbell (in kg)
    """
    if total_weight < bar_weight:
        raise ValueError("Total weight must be greater than or equal to the bar weight.")
    
    weight_to_load = (total_weight - bar_weight) / 2
    return weight_to_load


def plate_selection(weight_to_load, plate_weights=[20, 10, 5, 2.5]):
    """
    Select the plates needed to load the specified weight on each side of the barbell.
    
    Args:
        weight_to_load: The weight to load on each side of the barbell (in kg)
        plate_weights: A list of available plate weights (default is [25, 20, 15, 10, 5, 2.5])
    
    Returns:
        A list of plates to load on each side of the barbell
    """
    selected_plates = []
    remaining_weight = weight_to_load
    
    for plate in plate_weights:
        while remaining_weight >= plate:
            selected_plates.append(plate)
            remaining_weight -= plate
            
    return selected_plates


def get_workout_data(target_weight):
    """
    Generate all warmup sets and target weight data.
    
    Args:
        target_weight: The total weight to be lifted (in kg)
    
    Returns:
        Dictionary with warmup sets and target weight data
    """
    # Calculate warmup weights
    w45, w65, w85 = calculate_warmup_weights(target_weight)
    
    data = {
        "warmup_sets": [
            {
                "set": "2 sets",
                "reps": 5,
                "weight": 20,
                "weight_per_side": 0,
                "plates": "None (just the bar)"
            },
            {
                "set": "1 set",
                "reps": 5,
                "weight": w45,
                "weight_per_side": round(plate_weight(w45), 2),
                "plates": plate_selection(plate_weight(w45))
            },
            {
                "set": "1 set",
                "reps": 3,
                "weight": w65,
                "weight_per_side": round(plate_weight(w65), 2),
                "plates": plate_selection(plate_weight(w65))
            },
            {
                "set": "1 set",
                "reps": 2,
                "weight": w85,
                "weight_per_side": round(plate_weight(w85), 2),
                "plates": plate_selection(plate_weight(w85))
            }
        ],
        "target": {
            "weight": target_weight,
            "weight_per_side": round(plate_weight(target_weight), 2),
            "plates": plate_selection(plate_weight(target_weight))
        }
    }
    
    return data


def print_weight_and_plates(target_weight):
    """
    Print all warmup sets with plate loading and the target weight with plate loading.
    
    Args:
        target_weight: The total weight to be lifted (in kg)
    """
    # Calculate warmup weights
    w45, w65, w85 = calculate_warmup_weights(target_weight)
    
    print("=" * 50)
    print("WARMUP SETS")
    print("=" * 50)
    
    # Print bar only
    print(f"\n2 sets of 5 reps - Bar only (20kg)")
    print(f"  Plates per side: None (just the bar)\n")
    
    # 45% warmup
    plates_45 = plate_selection(plate_weight(w45))
    print(f"1 set of 5 reps - {w45}kg")
    print(f"  Weight to load per side: {plate_weight(w45)}kg")
    print(f"  Plates per side: {plates_45}\n")
    
    # 65% warmup
    plates_65 = plate_selection(plate_weight(w65))
    print(f"1 set of 3 reps - {w65}kg")
    print(f"  Weight to load per side: {plate_weight(w65)}kg")
    print(f"  Plates per side: {plates_65}\n")
    
    # 85% warmup
    plates_85 = plate_selection(plate_weight(w85))
    print(f"1 set of 2 reps - {w85}kg")
    print(f"  Weight to load per side: {plate_weight(w85)}kg")
    print(f"  Plates per side: {plates_85}\n")
    
    # Target weight
    print("=" * 50)
    print("TARGET WEIGHT")
    print("=" * 50)
    plates_target = plate_selection(plate_weight(target_weight))
    print(f"\n{target_weight}kg")
    print(f"  Weight to load per side: {plate_weight(target_weight)}kg")
    print(f"  Plates per side: {plates_target}")



@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')


@app.route('/api/calculate', methods=['POST'])
def calculate():
    """API endpoint to calculate warmup weights and plates."""
    try:
        data = request.get_json()
        target_weight = float(data.get('target_weight'))
        
        if target_weight <= 0:
            return jsonify({'error': 'Target weight must be greater than 0'}), 400
        
        workout_data = get_workout_data(target_weight)
        return jsonify(workout_data)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid target weight'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else 5042
    app.run(debug=True, port=port)
