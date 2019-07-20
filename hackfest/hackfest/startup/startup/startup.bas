10 REM  startup.bas
20 REM startup
30 REM Created by Kris Kennaway on 19/07/2019.
40 REM  Copyright © 2019 Kris Kennaway. All rights reserved.

10 un$ = "UnCoLoUrS": ul=len(un$)
20 kk$ = "kRiS kEnNaWaY": kl=len(kk$)

30 dim un%(ul): dim kk%(kl)
40 for i =1 to ul: uu%(i) = asc(mid$(un$, i, 1)): next

40 for i =1 to kl: kk%(i) = asc(mid$(kk$, i, 1)): next

100 print chr$(4); "pr#3"
105 REM display header
110 vtab 1: x$=un$: xl=ul: gosub 10000
150 vtab 2: x$=kk$: xl=kl: gosub 10000

199 REM print intro text, while ticking speaker (1-bit S0UNDZZZZZZ) and toggling case in header
200 read a$
210 if a$ = "" then 500
220 for i = 1 to 1000: next: rem delay
230 print:print
235 ht = 0
240 for i = 1 to len(a$): poke -16336,0: print mid$(a$,i,1);:ht = ht + 1

241 if ht = 80 then ht = 0

242 if int(i / 5) <> i / 5 then 325
245 vt=peek(37) + 1

250 cp = int(rnd(1)*ul) + 1
260 c = un%(cp)
270 if c >= 65 and c <= 90 then un%(cp) = c + 32
280 if c >= 97 and c <= 122 then un%(cp) = c - 32
291 vtab 1: htab 40-ul + cp * 2 - 2: print chr$(un%(cp))

300 cp = int(rnd(1)*kl) + 1
301 c = kk%(cp)
303 if c >= 65 and c <= 90 then kk%(cp) = c + 32
304 if c >= 97 and c <= 122 then kk%(cp) = c - 32
306 vtab 2: htab 40-kl + cp * 2 - 2: print chr$(kk%(cp))

320 vtab vt: htab ht + 1
325 next i

330 goto 200

500 get k$
504 REM routine to init DHGR and move $4000-$5FFF into $2000-$3FFF
505 print chr$(4); "bload hackfest"
509 REM cycle image loading
510 print chr$(4); "bload uncolours"
520 call 24576
530 for i=1 to 5000: next

540 print chr$(4); "bload kfest"
555 call 24576

560 for i=1 to 5000: next

570 print chr$(4); "bload apple"
585 call 24576

590 for i=1 to 5000: next

600 print chr$(4); "bload yinyang"
615 call 24576

620 for i=1 to 5000: next

700 print chr$(4); "bload skull"
715 call 24576

720 for i=1 to 5000: next

800 print chr$(4); "bload penguin"
815 call 24576

820 for i=1 to 5000: next


900 goto 510

1000 data "This demo exploits colour artifacts that aren't supported by most emulators."
1010 data "Try in OpenEmulator or on a composite colour monitor."
1020 data "(or compare to other emulators to check these really are 'colour' images)"
1030 data "In my lightning talk I described how to understand Double-Hires colours in terms of a 4-bit sliding window across the 560 horizontal dots."
1040 data "Sequences of 4 dots produce one of 16 colours, for each of the 560 dots."
1050 data "This is only an approximation."
1060 data "This demo shows what happens when the approximation breaks down..."

1070 data "Carefully chosen sequences of dots pack the colours too tightly and they cancel"

1085 data "This gives more levels of grey than usually available, but only in certain patterns."

1080 data "Press any key to continue..."
1999 data ""

10000 htab 40 - xl: for x=1 to xl:print mid$(x$,x,1) " ";: next:return
