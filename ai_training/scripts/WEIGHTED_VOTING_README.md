# Weighted Voting System - Implementation Documentation

## Overview

The consensus_voting_interactive.py script has been enhanced with a weighted voting system that assigns different scores to different annotators based on their expertise or reliability.

## User Weights

The following users have custom weights:

| Username | Weight | Description |
|----------|--------|-------------|
| nhhoangthong | 1.5 | Highest priority annotator |
| dangdoai3 | 1.4 | High priority annotator |
| ah3cu102 | 1.3 | Medium-high priority annotator |
| quangvinh02200 | 1.2 | Medium priority annotator |
| (others) | 1.0 | Default weight for all other users |

## How It Works

### Highest-Weighted User Selection

When there is disagreement among annotators, the system uses a simple rule:

**Pick the vote from the annotator with the highest weight**

Example:
- If nhhoangthong (1.5) votes "Negative" and others vote "Positive"
- Result: "Negative" (nhhoangthong has highest weight)

This ensures the most trusted/experienced annotator's decision is always respected.

### Example Scenarios

#### Scenario 1: All Agree
- nhhoangthong (1.5): Positive
- dangdoai3 (1.4): Positive  
- ah3cu102 (1.3): Positive

**Result**: Positive (everyone agrees)
- No disagreement, consensus accepted automatically

#### Scenario 2: Highest Weight User Overrides Majority
- nhhoangthong (1.5): Negative
- dangdoai3 (1.4): Positive
- quangvinh02200 (1.2): Positive

**Simple majority**: Positive (2 votes vs 1 vote)
**Highest weight**: nhhoangthong (1.5) voted Negative

**Result**: Negative wins (nhhoangthong has highest weight)
- In auto mode: automatically selects Negative
- In interactive mode: shows suggestion, manager can override

#### Scenario 3: All Different Votes
- nhhoangthong (1.5): Negative
- dangdoai3 (1.4): Positive
- ah3cu102 (1.3): Neutral

**Result**: Negative wins (nhhoangthong has highest weight)

## Usage

### Auto Mode (Automatic Weighted Voting)
```bash
python consensus_voting_interactive.py data_label/2.csv --auto
```
- Automatically uses weighted voting to resolve conflicts
- No manual intervention required

### Interactive Mode (Manual Review with Weighted Suggestions)
```bash
python consensus_voting_interactive.py data_label/2.csv
```
- Shows both simple count and weighted scores
- Suggests weighted winner
- Manager can override if needed

### Disable Weighted Voting
```bash
python consensus_voting_interactive.py data_label/2.csv --no-weighted
```
- Falls back to simple majority voting
- Uses priority order (Negative > Neutral > Positive) for conflicts

## Command Line Options

| Option | Description |
|--------|-------------|
| --auto | Auto mode: uses weighted voting without asking |
| --no-weighted | Disable weighted voting, use simple majority |
| --min-agreement N | Minimum vote count required (1-3, default: 2) |
| --review-all | Review all cases without sufficient agreement |

## Display Features

When weighted voting is active, the system displays:

1. **Annotator votes with weights**:
   ```
   1. nhhoangthong      → Positive        (weight: 1.5)
   2. dangdoai3         → Negative        (weight: 1.4)
   3. ah3cu102          → Positive        (weight: 1.3)
   ```

2. **Simple count statistics**:
   ```
   Positive        : 2/3 (67%)
   Negative        : 1/3 (33%)
   ```

3. **Weighted scores** (when there's disagreement):
   ```
   Weighted Scores:
   Positive        : 2.8/4.2 (67%)
   Negative        : 1.4/4.2 (33%)
   
   Winner (Weighted): Positive (score: 2.8)
   ```

## Edge Cases Handled

1. **Unknown users**: Get default weight of 1.0
2. **Empty annotations**: Returns empty string with confidence 1.0
3. **Perfect agreement**: Bypasses weighted voting (all agree anyway)
4. **Conflict between simple and weighted**: Shows both, suggests weighted winner
5. **Ties in weighted scores**: First value in sorted order wins (deterministic)

## Technical Implementation

### New Functions

1. `get_user_weight(annotator)`: Extract username and return weight
2. `weighted_vote(values, annotations)`: Calculate weighted voting result
   - Returns: (winning_value, winning_weight, weight_details)

### Modified Functions

1. `display_annotations()`: Now shows weights and weighted scores
2. `majority_vote_with_review()`: Incorporates weighted voting logic
3. `consensus_with_manager_review()`: Added use_weighted parameter
4. `main()`: Added --no-weighted option

## Testing

Run the test suite to verify implementation:
```bash
python scripts/test_weighted_voting.py
```

All tests should pass, verifying:
- User weight retrieval
- Weighted score calculation
- Conflict resolution
- Edge case handling

## Backup

A backup of the original file was created at:
```
D:/AI_Tranning/ai_training/scripts/consensus_voting_interactive.py.backup
```

## Notes

- Weights are case-insensitive (usernames converted to lowercase)
- Email format supported: extracts username before '@' symbol
- System maintains backward compatibility with --no-weighted flag
- Default behavior: weighted voting enabled
