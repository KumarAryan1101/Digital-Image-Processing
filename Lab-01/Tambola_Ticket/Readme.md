# Tambola / Housie Ticket Generator

This lab demonstrates matrix generation, logical filtering, sorting, and graphical plot operations in MATLAB by designing a standard Tambola / Housie ticket generator.

## Game Rules & Constraints

A valid Tambola ticket must adhere to the following structural constraints:
1. **Dimensions:** The ticket is a grid of 3 rows and 9 columns (27 cells in total).
2. **Number Count:** Exactly 15 numbers are distributed across the grid.
3. **Row Constraint:** Every row contains exactly 5 numbers and 4 blank spaces.
4. **Column Constraint:** Every column contains at least 1 number and at most 3 numbers.
5. **Standard Ranges:** Numbers in columns follow specific range groupings:
   - Column 1: $1 - 9$
   - Column 2: $10 - 19$
   - Column 3: $20 - 29$
   - Column 4: $30 - 39$
   - Column 5: $40 - 49$
   - Column 6: $50 - 59$
   - Column 7: $60 - 69$
   - Column 8: $70 - 79$
   - Column 9: $80 - 90$
6. **Sorting:** Numbers in each column must be sorted in ascending order from top to bottom.
7. **Uniqueness:** No duplicate numbers are allowed in a single ticket.

---

## Code Overview

The script [`Tambola_Ticket.m`](Tambola_Ticket.m) implements the generation algorithm:
1. **Grid Allocation:** Generates random binary layouts until one meets the exact row and column sum constraints.
2. **Value Assignment:** Picks random unique values matching the standard range for each column.
3. **Sorting:** Sorts values in each column to maintain the ascending top-to-bottom rule.
4. **Visualization:** Draws the ticket grid graphically using MATLAB's `rectangle` and `text` plotting functions.

---

## File Structure

| File Name | Description |
| :--- | :--- |
| [`Tambola_Ticket.m`](Tambola_Ticket.m) | Main MATLAB generator and drawing script |
| [`Tambola_Ticket.png`](Tambola_Ticket.png) | Graphical output example of the generated ticket |

---

## How to Run

1. Open MATLAB.
2. Navigate to this directory:
   ```matlab
   cd('Lab-01/Tambola_Ticket')
   ```
3. Run the script:
   ```matlab
   Tambola_Ticket
   ```
