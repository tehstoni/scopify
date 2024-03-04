import ipaddress
import argparse

def read_ips_from_file(file_path):
    """Read IP addresses or ranges from a file."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def normalize_ip_range(ip_range):
    """Normalize different IP range formats into a list of individual IP addresses."""
    if '-' in ip_range:
        if ' - ' in ip_range:
            start_ip, end_ip = ip_range.split(' - ')
        else:
            start_ip, end_ip = ip_range.split('-')
        start_ip = ipaddress.ip_address(start_ip)
        end_ip = ipaddress.ip_address(end_ip)
        return [str(ip) for ip in ipaddress.summarize_address_range(start_ip, end_ip)]
    else:
        return [str(ip) for ip in ipaddress.ip_network(ip_range, strict=False)]

def exclude_out_of_scope(inscope, outofscope):
    """Generate in-scope IPs, exclude out-of-scope IPs, and return optimized IP list."""
    in_scope_ips = set()
    out_scope_ips = set()

    for ip_range in inscope:
        in_scope_ips.update(normalize_ip_range(ip_range))

    for ip_range in outofscope:
        out_scope_ips.update(normalize_ip_range(ip_range))

    final_ips = in_scope_ips - out_scope_ips

    return list(final_ips)

def ip_list_to_ranges(ip_list):
    """Convert a list of IPs back into condensed ranges or CIDR blocks."""
    ip_list = sorted(ip_list, key=lambda ip: int(ipaddress.ip_address(ip)))
    ranges = []

    def add_range(start, end):
        """Add range to list in the appropriate format."""
        if start == end:
            ranges.append(str(start))
        else:
            # Attempt to summarize the range into CIDR blocks
            try:
                cidr = ipaddress.summarize_address_range(ipaddress.ip_address(start), ipaddress.ip_address(end))
                ranges.extend([str(block) for block in cidr])
            except ValueError:
                # Fallback to dash notation if it cannot be summarized into CIDR blocks
                ranges.append(f"{start}-{end}")

    if not ip_list:
        return ranges  # Return early if the list is empty

    start_ip = end_ip = ipaddress.ip_address(ip_list[0])

    for ip in ip_list[1:]:
        ip = ipaddress.ip_address(ip)
        if int(ip) - int(end_ip) == 1:
            end_ip = ip
        else:
            add_range(start_ip, end_ip)
            start_ip = end_ip = ip

    # Add the last range
    add_range(start_ip, end_ip)

    return ranges



def main():
    parser = argparse.ArgumentParser(description='Process in-scope and out-of-scope IP addresses from files.')
    parser.add_argument('-i', '--inscope', type=str, help='File with in-scope IP ranges or addresses', required=True)
    parser.add_argument('-e', '--exclude', type=str, help='File with out-of-scope IP ranges or addresses', required=True)
    parser.add_argument('-o', '--output', type=str, help='Output file to save the results', required=True)

    args = parser.parse_args()

    # Read IPs from files
    inscope_ips = read_ips_from_file(args.inscope)
    outofscope_ips = read_ips_from_file(args.exclude)

    final_ips = exclude_out_of_scope(inscope_ips, outofscope_ips)
    optimized_output = ip_list_to_ranges(final_ips)

    with open(args.output, 'w') as f:
        for line in optimized_output:
            f.write(f"{line}\n")

    print(f"Processed IPs are saved in {args.output}")

if __name__ == "__main__":
    main()
