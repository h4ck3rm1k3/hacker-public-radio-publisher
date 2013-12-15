echo example 
python ../hacker_public_radio.py --create test3 \
    --shownotes='here are some notes'   --series="Testing" --tag=Funky --tag=Soul \
    --title="My test show from the command line with a very long title\
that will be truncated for twitter to 144 chars......\
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890" \
--shownotes-load --save  --emit-html --print-config 

