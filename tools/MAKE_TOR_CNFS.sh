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

if [ ! -d ${TOR_DIR} ]; then
    echo You didn\'t install tor or invaild path of tor, please check ./confing;
    exit 0;
fi

CNF_DIR=${TOR_DIR}${CNF_DIR_NAME};
if [ ! -d $CNF_DIR ];then
    mkdir $CNF_DIR;
fi

rm ${CNF_DIR}torrc.*;

i=0
for port in `cat ports`;
do

    if [ $((i%2)) = 0 ]; then
        filename=${CNF_DIR}torrc.$((i/2))
        echo SocksPort $port > $filename;
    else
        echo ControlPort $port >> $filename;
        echo DataDirectory /var/lib/tor$((i/2)) >> $filename;
        cat additional_cnf >> $filename
    fi
    ((i ++))
done
echo Creation\(Update\) of $((i/2)) config file\(s\) under ${CNF_DIR} is completed.;

