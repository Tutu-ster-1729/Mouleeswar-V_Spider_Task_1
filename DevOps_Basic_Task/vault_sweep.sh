#!/bin/bash

TARGET="$1"
LOGFILE="vault_sweep.log"

log_message() {
    LEVEL="$1"
    MESSAGE="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$LEVEL] $MESSAGE" >> "$LOGFILE"
}

while read file
do
    echo "Found: $file"
    if grep -Eq "rm -rf|mkfs|shutdown|reboot" "$file"
    then 
	echo "[WARN] $file - Dangerous command found"
        log_message "WARN" "$file - Dangerous command found"
    fi

    if grep -Eq "curl.*\|.*(sh|bash)|wget.*\|.*(sh|bash)" "$file"
    then
	echo "[WARN] $file - Suspicious download execution"
	log_message "WARN" "$file - contains curl/wget pipe execution"
    fi

    PERMS=$(stat -c "%a" "$file")
    if [[ "$PERMS" == 777 ]]
    then
        echo "[WARN] $file - World writable permissions"
        log_message "WARN" "$file - has world writable permissions"

        read -p "Fix permissions? (y/n): " choice < /dev/tty
        if [[ "$choice" == "y" ]]
        then 
            chmod o-w "$file"
	    log_message "FIX" "$file - removed world write permissions"
        fi

    fi

done < <(find "$TARGET" -type f -name "*.sh")

while read envfile
do 
    echo "Checking $envfile"
    OUTPUT="$envfile.sanitized"
    valid_count=0
    invalid_count=0
    > "$OUTPUT"
    while read line
    do
	if [[ "$line" =~ ^[A-Za-z0-9_]*= ]]
	then

	    if [[ "$line" =~ \" ]]
	    then
		((invalid_count++))
		continue
	    fi

	    if [[ "$line" =~ ^(PASSWORD|TOKEN|SECRET)= ]]
       	    then
		log_message "WARN" "$envfile - removed sensitive variable"
		((invalid_count++))
		continue
	    fi

	    if [[ "$line" =~ ^PATH= ]] || [[ "$line" =~ ^export[[:space:]]+PATH ]]
	    then
		((invalid_count++))
		continue
	    fi

	    echo "$line" >> "$OUTPUT"
	    ((valid_count++))
	
	else
	    ((invalid_count++))
	fi

    done < "$envfile"
    
    echo "[INFO] Created $OUTPUT"
    echo "[INFO] $envfile Valid: $valid_count, Invalid: $invalid_count"
    log_message "INFO" "Created $OUTPUT"
    log_message "INFO" "$envfile Valid: $valid_count, Invalid: $invalid_count"

done < <(find "$TARGET" -type f -name ".env*")
