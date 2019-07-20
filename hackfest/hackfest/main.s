;
;  main.s
;  hackfest
;
;  Created by Kris Kennaway on 17/07/2019.
;  Copyright © 2019 Kris Kennaway. All rights reserved.
;

.include "apple2.inc"

STORE80ON = $c001
DHIRESON = $c05e
COL80ON = $c00d
HIRESON = $c057
TEXTOFF = $c050
PAGE2OFF = $c054
PAGE2ON = $c055


.proc main
    STA DHIRESON
    STA HIRESON
    STA TEXTOFF
    STA COL80ON

    STA STORE80ON
    STA PAGE2ON
   
    ; self-initialize so we can run multiple times
    LDA #$1F
    STA @d1+1
    LDA #$FF
    STA @d2+1
    
@d1:
    LDX #$1F
@d2:
    LDY #$FF
    
loop0:

    txa
    ADC #$20
    STA @d2+2
    ADC #$20
    STA @d1+2
@d1:
    LDA $ff00,y
@d2:
    STA $ff00,y

    DEY
    BEQ @0
    BRA loop0

@0:
    CPX #$00
    BEQ @1

    DEX
    BRA loop0

@1:
    ; done
    STA PAGE2OFF
    RTS
.endproc
