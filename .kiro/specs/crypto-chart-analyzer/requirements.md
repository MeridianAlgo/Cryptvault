# Requirements Document

## Introduction

This feature implements a cryptocurrency chart pattern analyzer that operates entirely in the terminal environment without requiring external APIs. The system will analyze price data to identify common technical analysis patterns including bullish continuation patterns (ascending triangles, bull flags, cup and handle), bearish continuation patterns (descending triangles, bear flags, falling channels), and divergence patterns. The analyzer will provide pattern recognition capabilities with visual terminal output and pattern confidence scoring.

## Requirements

### Requirement 1

**User Story:** As a cryptocurrency trader, I want to analyze price data for chart patterns in the terminal, so that I can identify trading opportunities without relying on external services.

#### Acceptance Criteria

1. WHEN the user provides price data THEN the system SHALL analyze the data for recognizable chart patterns
2. WHEN price data is analyzed THEN the system SHALL display results in a terminal-friendly format
3. WHEN patterns are detected THEN the system SHALL provide confidence scores for each identified pattern
4. IF no clear patterns are found THEN the system SHALL inform the user that no significant patterns were detected

### Requirement 2

**User Story:** As a trader, I want to identify bullish continuation patterns, so that I can spot potential upward price movements.

#### Acceptance Criteria

1. WHEN analyzing price data THEN the system SHALL detect ascending triangle patterns
2. WHEN analyzing price data THEN the system SHALL detect bull flag patterns
3. WHEN analyzing price data THEN the system SHALL detect bull pennant patterns
4. WHEN analyzing price data THEN the system SHALL detect cup and handle patterns
5. WHEN analyzing price data THEN the system SHALL detect rising channel/trend channel patterns
6. WHEN analyzing price data THEN the system SHALL detect measured move up patterns
7. WHEN analyzing price data THEN the system SHALL detect rising wedge patterns
8. WHEN analyzing price data THEN the system SHALL detect rectangle/consolidation patterns (bullish breakout)
9. WHEN a bullish pattern is detected THEN the system SHALL classify it as "Bullish Continuation"

### Requirement 3

**User Story:** As a trader, I want to identify bearish continuation patterns, so that I can spot potential downward price movements.

#### Acceptance Criteria

1. WHEN analyzing price data THEN the system SHALL detect descending triangle patterns
2. WHEN analyzing price data THEN the system SHALL detect bear flag patterns
3. WHEN analyzing price data THEN the system SHALL detect bear pennant patterns
4. WHEN analyzing price data THEN the system SHALL detect inverted cup and handle patterns
5. WHEN analyzing price data THEN the system SHALL detect falling channel/trend channel patterns
6. WHEN analyzing price data THEN the system SHALL detect falling wedge patterns
7. WHEN analyzing price data THEN the system SHALL detect rectangle/consolidation patterns (bearish breakdown)
8. WHEN a bearish pattern is detected THEN the system SHALL classify it as "Bearish Continuation"

### Requirement 4

**User Story:** As a trader, I want to identify divergence patterns, so that I can spot potential trend reversals.

#### Acceptance Criteria

1. WHEN analyzing price and indicator data THEN the system SHALL detect bearish divergence patterns
2. WHEN analyzing price and indicator data THEN the system SHALL detect bullish divergence patterns
3. WHEN divergence is detected THEN the system SHALL indicate the type of divergence (regular or hidden)
4. WHEN divergence is detected THEN the system SHALL provide the timeframe over which the divergence occurs

### Requirement 5

**User Story:** As a user, I want to input price data from various sources, so that I can analyze different cryptocurrencies and timeframes.

#### Acceptance Criteria

1. WHEN the user provides CSV price data THEN the system SHALL parse and validate the data format
2. WHEN the user provides JSON price data THEN the system SHALL parse and validate the data format
3. IF price data is missing required fields THEN the system SHALL display clear error messages
4. WHEN price data is loaded THEN the system SHALL display basic statistics (date range, number of data points)
5. WHEN invalid data format is provided THEN the system SHALL suggest the correct format requirements

### Requirement 6

**User Story:** As a user, I want to see visual representations of detected patterns in the terminal, so that I can understand the pattern context.

#### Acceptance Criteria

1. WHEN patterns are detected THEN the system SHALL display ASCII-based price charts
2. WHEN patterns are detected THEN the system SHALL highlight pattern boundaries on the chart
3. WHEN displaying charts THEN the system SHALL include price levels and time indicators
4. WHEN multiple patterns are found THEN the system SHALL display them in order of confidence
5. IF the terminal supports colors THEN the system SHALL use colors to differentiate pattern types

### Requirement 7

**User Story:** As a trader, I want to configure pattern detection sensitivity, so that I can adjust the analyzer for different market conditions.

#### Acceptance Criteria

1. WHEN the user specifies sensitivity settings THEN the system SHALL adjust pattern detection thresholds
2. WHEN high sensitivity is selected THEN the system SHALL detect more potential patterns with lower confidence
3. WHEN low sensitivity is selected THEN the system SHALL detect fewer patterns with higher confidence
4. WHEN no sensitivity is specified THEN the system SHALL use default medium sensitivity settings
5. WHEN sensitivity settings are changed THEN the system SHALL re-analyze the data with new parameters

### Requirement 8

**User Story:** As a trader, I want to identify bullish reversal patterns, so that I can spot potential trend changes from bearish to bullish.

#### Acceptance Criteria

1. WHEN analyzing price data THEN the system SHALL detect double bottom patterns
2. WHEN analyzing price data THEN the system SHALL detect triple bottom patterns
3. WHEN analyzing price data THEN the system SHALL detect inverse head and shoulders patterns
4. WHEN analyzing price data THEN the system SHALL detect falling wedge reversal patterns
5. WHEN analyzing price data THEN the system SHALL detect hammer and doji candlestick reversal patterns
6. WHEN analyzing price data THEN the system SHALL detect morning star patterns
7. WHEN analyzing price data THEN the system SHALL detect bullish engulfing patterns
8. WHEN a bullish reversal pattern is detected THEN the system SHALL classify it as "Bullish Reversal"

### Requirement 9

**User Story:** As a trader, I want to identify bearish reversal patterns, so that I can spot potential trend changes from bullish to bearish.

#### Acceptance Criteria

1. WHEN analyzing price data THEN the system SHALL detect double top patterns
2. WHEN analyzing price data THEN the system SHALL detect triple top patterns
3. WHEN analyzing price data THEN the system SHALL detect head and shoulders patterns
4. WHEN analyzing price data THEN the system SHALL detect rising wedge reversal patterns
5. WHEN analyzing price data THEN the system SHALL detect shooting star and gravestone doji patterns
6. WHEN analyzing price data THEN the system SHALL detect evening star patterns
7. WHEN analyzing price data THEN the system SHALL detect bearish engulfing patterns
8. WHEN a bearish reversal pattern is detected THEN the system SHALL classify it as "Bearish Reversal"

### Requirement 10

**User Story:** As a trader, I want to identify bilateral patterns, so that I can prepare for breakouts in either direction.

#### Acceptance Criteria

1. WHEN analyzing price data THEN the system SHALL detect symmetrical triangle patterns
2. WHEN analyzing price data THEN the system SHALL detect diamond patterns
3. WHEN analyzing price data THEN the system SHALL detect rectangle/box patterns
4. WHEN analyzing price data THEN the system SHALL detect expanding triangle (broadening) patterns
5. WHEN analyzing price data THEN the system SHALL detect pennant patterns (neutral)
6. WHEN a bilateral pattern is detected THEN the system SHALL classify it as "Bilateral/Neutral"

### Requirement 11

**User Story:** As a trader, I want to identify advanced harmonic patterns, so that I can spot complex geometric price relationships.

#### Acceptance Criteria

1. WHEN analyzing price data THEN the system SHALL detect Gartley patterns (222 pattern)
2. WHEN analyzing price data THEN the system SHALL detect Butterfly patterns
3. WHEN analyzing price data THEN the system SHALL detect Bat patterns
4. WHEN analyzing price data THEN the system SHALL detect Crab patterns
5. WHEN analyzing price data THEN the system SHALL detect ABCD patterns
6. WHEN analyzing price data THEN the system SHALL detect Cypher patterns
7. WHEN a harmonic pattern is detected THEN the system SHALL provide Fibonacci retracement levels
8. WHEN a harmonic pattern is detected THEN the system SHALL classify it as "Harmonic Pattern"

### Requirement 12

**User Story:** As a trader, I want to identify candlestick patterns, so that I can understand short-term price action signals.

#### Acceptance Criteria

1. WHEN analyzing price data THEN the system SHALL detect single candlestick patterns (hammer, shooting star, doji, spinning top)
2. WHEN analyzing price data THEN the system SHALL detect two-candlestick patterns (engulfing, harami, piercing line, dark cloud cover)
3. WHEN analyzing price data THEN the system SHALL detect three-candlestick patterns (morning star, evening star, three white soldiers, three black crows)
4. WHEN analyzing price data THEN the system SHALL detect continuation patterns (rising/falling three methods, upside/downside gap three methods)
5. WHEN candlestick patterns are detected THEN the system SHALL provide pattern reliability based on market context
6. WHEN candlestick patterns are detected THEN the system SHALL classify them by bullish/bearish/neutral sentiment

### Requirement 13

**User Story:** As a user, I want to save and load analysis results, so that I can review patterns over time.

#### Acceptance Criteria

1. WHEN analysis is complete THEN the system SHALL offer to save results to a file
2. WHEN the user chooses to save THEN the system SHALL create a timestamped analysis report
3. WHEN the user loads a previous analysis THEN the system SHALL display the saved pattern results
4. WHEN saving results THEN the system SHALL include pattern details, confidence scores, and timestamps
5. IF save location is not writable THEN the system SHALL suggest alternative save locations