for i in `cat ./config`;
do
    if [ $i = "TOR_DIR" ] || [ $i = "CNF_DIR_NAME" ]; then
        title=$i;
    else
        if [ $title = "TOR_DIR" ]; then
            TOR_DIR=$i;
        fi
        if [ $title = "CNF_DIR_NAME" ]; then
            CNF_DIR_NAME=$i;
        fi
        title="";
    fi
done

CNF_DIR=${TOR_DIR}${CNF_DIR_NAME};
cnf_num=`ls ${CNF_DIR}| wc -w`;

i=1;
for CNF_FILE in `ls ${CNF_DIR}`;
do
    sudo tor -f ${CNF_DIR}${CNF_FILE} > /dev/null 2>&1 &
    echo The tor is about to be started\[${i}/${cnf_num}\];
    ((i ++));
done
echo Wait a while for tor to activate.
